"""YAML-based agent configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class LLMConfig:
    """Configuration for an OpenAI-compatible LLM backend."""

    base_url: str = "http://localhost:11434/v1"
    model: str = "llama3"
    api_key: str = "not-needed"
    temperature: float = 0.7
    max_tokens: int = 4096
    supports_tools: bool = False
    timeout: int = 120


@dataclass
class SkillConfig:
    """Configuration for an agent skill."""

    id: str = ""
    name: str = ""
    description: str = ""
    tags: list[str] = field(default_factory=list)
    input_modes: list[str] = field(default_factory=lambda: ["text/plain"])
    output_modes: list[str] = field(default_factory=lambda: ["text/plain"])
    examples: list[str] = field(default_factory=list)


@dataclass
class NodeConfig:
    """Network node configuration."""

    role: str = "slave"  # "master" or "slave"
    name: str = "mesh-agent"
    host: str = "0.0.0.0"
    port: int = 10000


@dataclass
class MasterConfig:
    """How to find the master node."""

    discover: bool = True
    url: str = ""


@dataclass
class DiscoveryConfig:
    """mDNS discovery configuration."""

    enabled: bool = True
    method: str = "mdns"
    service_type: str = "_a2a-mesh._tcp.local."


@dataclass
class OrchestratorConfig:
    """Master orchestrator configuration."""

    auto_approve: bool = False
    auto_approve_skills: list[str] = field(default_factory=list)
    require_approval_skills: list[str] = field(default_factory=list)
    default_autonomy: int = 1
    approval_timeout: int = 300


@dataclass
class FileShareConfig:
    """Networked file share configuration."""

    enabled: bool = True
    root: str = "/tmp/mesh-workspace"
    port: int = 9001
    mount: str = "/workspace"


@dataclass
class UIConfig:
    """Web UI configuration."""

    enabled: bool = True
    port: int = 8080


@dataclass
class IntegrationConfig:
    """External tool integration configuration."""

    type: str = ""  # "claude_code", "aider", "qwen_code", "generic_cli"
    command: str = ""
    args: list[str] = field(default_factory=list)
    workspace_dir: str = ""
    timeout: int = 300
    environment: dict[str, str] = field(default_factory=dict)


@dataclass
class AgentConfig:
    """Complete agent configuration loaded from YAML."""

    node: NodeConfig = field(default_factory=NodeConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    skills: list[SkillConfig] = field(default_factory=list)
    system_prompt: str = "You are a helpful AI agent."
    master: MasterConfig = field(default_factory=MasterConfig)
    discovery: DiscoveryConfig = field(default_factory=DiscoveryConfig)
    orchestrator: OrchestratorConfig = field(default_factory=OrchestratorConfig)
    fileshare: FileShareConfig = field(default_factory=FileShareConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    integration: IntegrationConfig = field(default_factory=IntegrationConfig)

    @classmethod
    def from_yaml(cls, path: str | Path) -> AgentConfig:
        """Load configuration from a YAML file."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path) as f:
            raw = yaml.safe_load(f)

        return cls._from_dict(raw or {})

    @classmethod
    def _from_dict(cls, data: dict[str, Any]) -> AgentConfig:
        """Build config from a dictionary, substituting env vars."""
        data = _expand_env_vars(data)

        config = cls()

        if "node" in data:
            config.node = NodeConfig(**data["node"])
        # Backward compat: top-level agent.name/port maps to node
        if "agent" in data:
            agent = data["agent"]
            config.node.name = agent.get("name", config.node.name)
            config.node.port = agent.get("port", config.node.port)
            config.node.host = agent.get("host", config.node.host)
            if "description" in agent:
                config.system_prompt = agent.get(
                    "system_prompt", config.system_prompt
                )

        if "llm" in data:
            config.llm = LLMConfig(**data["llm"])

        if "skills" in data:
            config.skills = [SkillConfig(**s) for s in data["skills"]]

        if "system_prompt" in data:
            config.system_prompt = data["system_prompt"]

        if "master" in data:
            config.master = MasterConfig(**data["master"])

        if "discovery" in data:
            config.discovery = DiscoveryConfig(**data["discovery"])

        if "orchestrator" in data:
            config.orchestrator = OrchestratorConfig(**data["orchestrator"])

        if "fileshare" in data:
            config.fileshare = FileShareConfig(**data["fileshare"])

        if "ui" in data:
            config.ui = UIConfig(**data["ui"])

        if "integration" in data:
            config.integration = IntegrationConfig(**data["integration"])

        return config


def _expand_env_vars(data: Any) -> Any:
    """Recursively expand ${ENV_VAR} references in config values."""
    if isinstance(data, str):
        if data.startswith("${") and data.endswith("}"):
            var_name = data[2:-1]
            return os.environ.get(var_name, data)
        return data
    if isinstance(data, dict):
        return {k: _expand_env_vars(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_expand_env_vars(v) for v in data]
    return data
