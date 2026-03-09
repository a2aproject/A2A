"""Star topology manager — join, leave, heartbeat."""

from __future__ import annotations

import asyncio
import logging

import httpx

from mesh.agent.config import AgentConfig
from mesh.network.discovery import MeshDiscovery
from mesh.network.models import MasterInfo, NodeInfo

logger = logging.getLogger(__name__)


class StarTopology:
    """Manages the star network topology.

    For master: accepts registrations, monitors health.
    For slave: discovers master, registers, heartbeats.
    """

    def __init__(self, config: AgentConfig):
        self.config = config
        self.role = config.node.role
        self.discovery = MeshDiscovery()
        self.master_url: str | None = None
        self.agent_id: str | None = None
        self._heartbeat_task: asyncio.Task | None = None

    async def start(self):
        """Start the topology manager."""
        if self.role == "master":
            await self._start_master()
        else:
            await self._start_slave()

    async def _start_master(self):
        """Master: announce via mDNS."""
        if self.config.discovery.enabled:
            await self.discovery.announce_master(
                name=self.config.node.name,
                host=self.config.node.host,
                port=self.config.node.port,
                node_id=self.config.node.name,
                registry_port=self.config.node.port,
                fileshare_port=self.config.fileshare.port if self.config.fileshare.enabled else 0,
            )
            logger.info("Master: Announced via mDNS")

    async def _start_slave(self):
        """Slave: discover master and register."""
        # Find master
        if self.config.master.discover:
            logger.info("Slave: Discovering master via mDNS...")
            master_info = await self.discovery.discover_master(timeout=10)
            if master_info:
                self.master_url = f"http://{master_info.host}:{master_info.port}"
            else:
                logger.warning("Slave: Master not found via mDNS")
        elif self.config.master.url:
            self.master_url = self.config.master.url

        if not self.master_url:
            logger.error("Slave: No master URL available. Running standalone.")
            return

        # Register with master
        await self._register()

        # Start heartbeat
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

        # Announce self via mDNS
        if self.config.discovery.enabled:
            await self.discovery.announce_agent(
                name=self.config.node.name,
                host=self.config.node.host,
                port=self.config.node.port,
                node_id=self.agent_id or self.config.node.name,
                role="slave",
            )

    async def _register(self):
        """Register this agent with the master."""
        skill_tags = []
        for skill in self.config.skills:
            skill_tags.extend(skill.tags)

        payload = {
            "name": self.config.node.name,
            "host": self.config.node.host,
            "port": self.config.node.port,
            "role": "slave",
            "llm_model": self.config.llm.model,
            "llm_provider": _infer_provider(self.config.llm.base_url),
            "skill_tags": list(set(skill_tags)),
        }

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{self.master_url}/registry/agents",
                    json=payload,
                    timeout=10,
                )
                data = resp.json()
                self.agent_id = data.get("agent_id")
                logger.info(
                    f"Slave: Registered with master as '{self.config.node.name}' "
                    f"(id: {self.agent_id})"
                )
            except Exception as e:
                logger.error(f"Slave: Failed to register with master: {e}")

    async def _heartbeat_loop(self):
        """Send heartbeat to master every 15 seconds."""
        while True:
            await asyncio.sleep(15)
            if not self.master_url or not self.agent_id:
                continue

            async with httpx.AsyncClient() as client:
                try:
                    await client.post(
                        f"{self.master_url}/registry/agents/{self.agent_id}/heartbeat",
                        timeout=5,
                    )
                except Exception as e:
                    logger.warning(f"Slave: Heartbeat failed: {e}")
                    # Try to re-register
                    await self._register()

    async def stop(self):
        """Clean shutdown: deregister and stop heartbeat."""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()

        # Deregister from master
        if self.master_url and self.agent_id:
            async with httpx.AsyncClient() as client:
                try:
                    await client.delete(
                        f"{self.master_url}/registry/agents/{self.agent_id}",
                        timeout=5,
                    )
                    logger.info("Slave: Deregistered from master")
                except Exception:
                    pass

        await self.discovery.stop()


def _infer_provider(base_url: str) -> str:
    """Infer LLM provider from base URL."""
    url = base_url.lower()
    if "11434" in url or "ollama" in url:
        return "ollama"
    if "8000" in url or "vllm" in url:
        return "vllm"
    if "1234" in url or "lmstudio" in url:
        return "lmstudio"
    if "openai" in url:
        return "openai"
    if "anthropic" in url:
        return "anthropic"
    return "unknown"
