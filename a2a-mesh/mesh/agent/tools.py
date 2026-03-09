"""Tool/function calling registry for agents."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Callable

logger = logging.getLogger(__name__)


@dataclass
class ToolDef:
    """Definition of a callable tool."""

    name: str
    description: str
    parameters: dict[str, Any]
    handler: Callable


class ToolRegistry:
    """Registry of tools available to an agent.

    Tools are exposed to the LLM as OpenAI-format function schemas
    and executed when the LLM makes a tool call.
    """

    def __init__(self):
        self._tools: dict[str, ToolDef] = {}

    def register(
        self,
        name: str,
        description: str,
        parameters: dict[str, Any],
        handler: Callable,
    ):
        """Register a tool.

        Args:
            name: Tool name (must be unique).
            description: What the tool does.
            parameters: JSON Schema for the tool's parameters.
            handler: Async or sync callable(kwargs) -> str.
        """
        self._tools[name] = ToolDef(
            name=name,
            description=description,
            parameters=parameters,
            handler=handler,
        )
        logger.info(f"Registered tool: {name}")

    def get_schemas(self) -> list[dict]:
        """Get OpenAI-format tool schemas for all registered tools."""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
            }
            for tool in self._tools.values()
        ]

    async def execute(self, name: str, arguments: dict[str, Any]) -> str:
        """Execute a tool by name with given arguments."""
        if name not in self._tools:
            return f"Unknown tool: {name}"

        tool = self._tools[name]
        try:
            if asyncio.iscoroutinefunction(tool.handler):
                result = await tool.handler(**arguments)
            else:
                result = tool.handler(**arguments)
            return str(result)
        except Exception as e:
            logger.error(f"Tool {name} failed: {e}")
            return f"Tool error: {e}"

    @property
    def names(self) -> list[str]:
        return list(self._tools.keys())

    def __len__(self) -> int:
        return len(self._tools)


def create_default_tools() -> ToolRegistry:
    """Create a ToolRegistry with built-in tools."""
    registry = ToolRegistry()

    registry.register(
        name="get_current_time",
        description="Get the current date and time",
        parameters={
            "type": "object",
            "properties": {},
            "required": [],
        },
        handler=_get_current_time,
    )

    return registry


def _get_current_time() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()
