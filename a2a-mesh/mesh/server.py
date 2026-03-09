"""Server factory — creates the ASGI app for master or slave nodes."""

from __future__ import annotations

import logging

from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.responses import JSONResponse

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCard,
    AgentCapabilities,
    AgentSkill,
)

from mesh.agent.config import AgentConfig
from mesh.agent.base import LLMClient
from mesh.agent.executor import MeshAgentExecutor
from mesh.agent.tools import create_default_tools

logger = logging.getLogger(__name__)


def _build_agent_card(config: AgentConfig) -> AgentCard:
    """Build an A2A AgentCard from config."""
    skills = [
        AgentSkill(
            id=s.id,
            name=s.name,
            description=s.description,
            tags=s.tags,
            examples=s.examples or [],
            inputModes=s.input_modes,
            outputModes=s.output_modes,
        )
        for s in config.skills
    ]

    return AgentCard(
        name=config.node.name,
        description=config.system_prompt[:200],
        url=f"http://{config.node.host}:{config.node.port}",
        version=config.node.name,
        capabilities=AgentCapabilities(streaming=True),
        defaultInputModes=["text/plain"],
        defaultOutputModes=["text/plain"],
        skills=skills,
    )


def _build_executor(config: AgentConfig) -> MeshAgentExecutor:
    """Build the agent executor from config."""
    llm = LLMClient(config.llm)
    tools = create_default_tools() if config.llm.supports_tools else None
    return MeshAgentExecutor(
        llm=llm,
        system_prompt=config.system_prompt,
        tools=tools,
    )


async def create_slave_server(config: AgentConfig) -> Starlette:
    """Create a slave node ASGI application.

    Runs:
    - A2A agent server (handles tasks from master or other agents)
    """
    agent_card = _build_agent_card(config)
    executor = _build_executor(config)

    handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
    )

    a2a_app = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=handler,
    )

    logger.info(f"Slave agent '{config.node.name}' ready on port {config.node.port}")
    return a2a_app.build()


async def create_master_server(config: AgentConfig) -> Starlette:
    """Create a master node ASGI application.

    Runs:
    - A2A agent server (master can also be an agent)
    - Agent registry API (/registry/)
    - File share API (/files/) if enabled
    - UI API (/api/) and UI proxy (/ui/) if enabled
    """
    # Build the A2A agent part
    agent_card = _build_agent_card(config)
    executor = _build_executor(config)

    handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
    )

    a2a_app = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=handler,
    )

    base_app = a2a_app.build()

    # Add registry routes
    from mesh.network.registry import create_registry_routes

    registry = create_registry_routes()
    for route in registry.routes:
        base_app.routes.append(route)

    logger.info(
        f"Master node '{config.node.name}' ready on port {config.node.port}"
    )
    return base_app
