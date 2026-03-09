"""File share client for agents to access the shared workspace."""

from __future__ import annotations

import logging

import httpx

logger = logging.getLogger(__name__)


class FileShareClient:
    """Client for accessing the mesh file share from any agent."""

    def __init__(self, server_url: str, agent_id: str = "unknown"):
        self.server_url = server_url.rstrip("/")
        self.agent_id = agent_id

    async def read(self, path: str) -> str:
        """Read file contents as string."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.server_url}/files/{path}",
                timeout=30,
            )
            resp.raise_for_status()
            return resp.text

    async def read_bytes(self, path: str) -> bytes:
        """Read file contents as bytes."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.server_url}/files/{path}",
                timeout=30,
            )
            resp.raise_for_status()
            return resp.content

    async def write(self, path: str, content: str) -> dict:
        """Write content to a file."""
        async with httpx.AsyncClient() as client:
            resp = await client.put(
                f"{self.server_url}/files/{path}",
                content=content.encode(),
                headers={"X-Agent-ID": self.agent_id},
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()

    async def write_bytes(self, path: str, content: bytes) -> dict:
        """Write binary content to a file."""
        async with httpx.AsyncClient() as client:
            resp = await client.put(
                f"{self.server_url}/files/{path}",
                content=content,
                headers={"X-Agent-ID": self.agent_id},
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()

    async def delete(self, path: str) -> dict:
        """Delete a file or directory."""
        async with httpx.AsyncClient() as client:
            resp = await client.delete(
                f"{self.server_url}/files/{path}",
                headers={"X-Agent-ID": self.agent_id},
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()

    async def list_dir(self, path: str = "") -> list[dict]:
        """List directory contents."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.server_url}/files/",
                params={"dir": path} if path else {},
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()

    async def search(self, query: str) -> list[dict]:
        """Search file contents."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.server_url}/files/",
                params={"search": query},
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()

    async def tree(self) -> dict:
        """Get full directory tree."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.server_url}/files/",
                params={"tree": "1"},
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()

    async def metadata(self, path: str) -> dict:
        """Get file metadata."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.server_url}/files/{path}",
                params={"meta": "1"},
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()


def create_fileshare_tools(client: FileShareClient):
    """Create tool definitions for the agent tool registry.

    Returns list of (name, description, parameters, handler) tuples.
    """
    return [
        (
            "read_file",
            "Read a file from the shared workspace",
            {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path relative to workspace root"},
                },
                "required": ["path"],
            },
            lambda path: client.read(path),
        ),
        (
            "write_file",
            "Write content to a file in the shared workspace",
            {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path relative to workspace root"},
                    "content": {"type": "string", "description": "Content to write"},
                },
                "required": ["path", "content"],
            },
            lambda path, content: client.write(path, content),
        ),
        (
            "list_files",
            "List files in a directory of the shared workspace",
            {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path (empty for root)", "default": ""},
                },
                "required": [],
            },
            lambda path="": client.list_dir(path),
        ),
        (
            "search_files",
            "Search for text content across all files in the shared workspace",
            {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Text to search for"},
                },
                "required": ["query"],
            },
            lambda query: client.search(query),
        ),
    ]
