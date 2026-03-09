"""Data models for network layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class NodeInfo:
    """Information about a node in the mesh."""

    node_id: str
    name: str
    host: str
    port: int
    role: str  # "master" or "slave"
    llm_model: str = ""
    llm_provider: str = ""
    url: str = ""
    healthy: bool = True
    last_heartbeat: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    registered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    skill_tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "name": self.name,
            "host": self.host,
            "port": self.port,
            "role": self.role,
            "url": self.url or f"http://{self.host}:{self.port}",
            "llm_model": self.llm_model,
            "llm_provider": self.llm_provider,
            "healthy": self.healthy,
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "registered_at": self.registered_at.isoformat(),
            "skill_tags": self.skill_tags,
        }


@dataclass
class MasterInfo:
    """Information about the master node discovered via mDNS."""

    host: str
    port: int
    node_id: str = ""
    name: str = ""
    registry_port: int = 0
    fileshare_port: int = 0


@dataclass
class ClusterStatus:
    """Overall cluster status."""

    master: NodeInfo | None = None
    agents: list[NodeInfo] = field(default_factory=list)
    total_agents: int = 0
    healthy_agents: int = 0
    total_tasks: int = 0

    def to_dict(self) -> dict:
        return {
            "master": self.master.to_dict() if self.master else None,
            "agents": [a.to_dict() for a in self.agents],
            "total_agents": self.total_agents,
            "healthy_agents": self.healthy_agents,
            "total_tasks": self.total_tasks,
        }
