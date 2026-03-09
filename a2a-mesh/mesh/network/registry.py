"""Agent registry — master-hosted service for tracking all agents."""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route, Router

from mesh.network.models import NodeInfo

logger = logging.getLogger(__name__)


class AgentRegistry:
    """In-memory registry of all agents in the mesh.

    Runs on the master node. Agents register/deregister via REST API.
    Heartbeat monitoring detects dead agents.
    """

    def __init__(self, dead_threshold_seconds: int = 45):
        self._agents: dict[str, NodeInfo] = {}
        self._dead_threshold = dead_threshold_seconds
        self._monitor_task: asyncio.Task | None = None

    def register(self, node_info: NodeInfo) -> str:
        """Register an agent. Returns agent_id."""
        if not node_info.node_id:
            node_info.node_id = str(uuid.uuid4())[:8]
        node_info.registered_at = datetime.now(timezone.utc)
        node_info.last_heartbeat = datetime.now(timezone.utc)
        node_info.healthy = True
        self._agents[node_info.node_id] = node_info
        logger.info(f"Registry: Registered agent '{node_info.name}' ({node_info.node_id})")
        return node_info.node_id

    def deregister(self, node_id: str) -> bool:
        """Remove an agent from the registry."""
        if node_id in self._agents:
            name = self._agents[node_id].name
            del self._agents[node_id]
            logger.info(f"Registry: Deregistered agent '{name}' ({node_id})")
            return True
        return False

    def heartbeat(self, node_id: str) -> bool:
        """Update heartbeat timestamp for an agent."""
        if node_id in self._agents:
            self._agents[node_id].last_heartbeat = datetime.now(timezone.utc)
            self._agents[node_id].healthy = True
            return True
        return False

    def get_agent(self, node_id: str) -> NodeInfo | None:
        return self._agents.get(node_id)

    def get_all_agents(self) -> list[NodeInfo]:
        return list(self._agents.values())

    def find_by_skill(self, skill_tag: str) -> list[NodeInfo]:
        """Find agents that have a specific skill tag."""
        return [
            agent
            for agent in self._agents.values()
            if skill_tag in agent.skill_tags and agent.healthy
        ]

    def find_by_role(self, role: str) -> list[NodeInfo]:
        return [a for a in self._agents.values() if a.role == role and a.healthy]

    async def start_health_monitor(self):
        """Start background task to check for dead agents."""
        self._monitor_task = asyncio.create_task(self._health_monitor_loop())

    async def _health_monitor_loop(self):
        while True:
            await asyncio.sleep(15)
            now = datetime.now(timezone.utc)
            for agent in self._agents.values():
                elapsed = (now - agent.last_heartbeat).total_seconds()
                if elapsed > self._dead_threshold:
                    if agent.healthy:
                        agent.healthy = False
                        logger.warning(
                            f"Registry: Agent '{agent.name}' ({agent.node_id}) "
                            f"marked unhealthy (no heartbeat for {elapsed:.0f}s)"
                        )

    async def stop(self):
        if self._monitor_task:
            self._monitor_task.cancel()


# ---- Singleton registry instance ----
_registry = AgentRegistry()


def get_registry() -> AgentRegistry:
    return _registry


# ---- Starlette REST API routes ----


async def handle_register(request: Request) -> JSONResponse:
    """POST /registry/agents — Register a new agent."""
    body = await request.json()
    node_info = NodeInfo(
        node_id=body.get("node_id", ""),
        name=body.get("name", "unknown"),
        host=body.get("host", request.client.host if request.client else "unknown"),
        port=body.get("port", 10000),
        role=body.get("role", "slave"),
        llm_model=body.get("llm_model", ""),
        llm_provider=body.get("llm_provider", ""),
        url=body.get("url", ""),
        skill_tags=body.get("skill_tags", []),
    )
    agent_id = _registry.register(node_info)
    return JSONResponse({"agent_id": agent_id, "status": "registered"})


async def handle_list_agents(request: Request) -> JSONResponse:
    """GET /registry/agents — List all agents. Supports ?skill= and ?role= filters."""
    skill = request.query_params.get("skill")
    role = request.query_params.get("role")

    if skill:
        agents = _registry.find_by_skill(skill)
    elif role:
        agents = _registry.find_by_role(role)
    else:
        agents = _registry.get_all_agents()

    return JSONResponse([a.to_dict() for a in agents])


async def handle_get_agent(request: Request) -> JSONResponse:
    """GET /registry/agents/{agent_id} — Get specific agent."""
    agent_id = request.path_params["agent_id"]
    agent = _registry.get_agent(agent_id)
    if not agent:
        return JSONResponse({"error": "Agent not found"}, status_code=404)
    return JSONResponse(agent.to_dict())


async def handle_deregister(request: Request) -> JSONResponse:
    """DELETE /registry/agents/{agent_id} — Deregister an agent."""
    agent_id = request.path_params["agent_id"]
    if _registry.deregister(agent_id):
        return JSONResponse({"status": "deregistered"})
    return JSONResponse({"error": "Agent not found"}, status_code=404)


async def handle_heartbeat(request: Request) -> JSONResponse:
    """POST /registry/agents/{agent_id}/heartbeat — Agent heartbeat."""
    agent_id = request.path_params["agent_id"]
    if _registry.heartbeat(agent_id):
        return JSONResponse({"status": "ok"})
    return JSONResponse({"error": "Agent not found"}, status_code=404)


async def handle_cluster_status(request: Request) -> JSONResponse:
    """GET /registry/status — Cluster status summary."""
    agents = _registry.get_all_agents()
    healthy = [a for a in agents if a.healthy]
    return JSONResponse({
        "total_agents": len(agents),
        "healthy_agents": len(healthy),
        "agents": [a.to_dict() for a in agents],
    })


def create_registry_routes() -> Router:
    """Create Starlette routes for the agent registry API."""
    return Router(
        routes=[
            Route("/registry/agents", handle_list_agents, methods=["GET"]),
            Route("/registry/agents", handle_register, methods=["POST"]),
            Route("/registry/agents/{agent_id}", handle_get_agent, methods=["GET"]),
            Route("/registry/agents/{agent_id}", handle_deregister, methods=["DELETE"]),
            Route(
                "/registry/agents/{agent_id}/heartbeat",
                handle_heartbeat,
                methods=["POST"],
            ),
            Route("/registry/status", handle_cluster_status, methods=["GET"]),
        ]
    )
