"""Generic CLI tool wrapper — base class for wrapping any CLI tool as an A2A agent."""

from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass, field
from typing import AsyncGenerator

logger = logging.getLogger(__name__)


@dataclass
class ToolResult:
    """Result from running a CLI tool."""

    output: str = ""
    errors: str = ""
    exit_code: int = 0
    files_changed: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return self.exit_code == 0

    def to_text(self) -> str:
        parts = []
        if self.output:
            parts.append(self.output)
        if self.errors:
            parts.append(f"\n[stderr]\n{self.errors}")
        if self.files_changed:
            parts.append(f"\n[Files changed: {', '.join(self.files_changed)}]")
        return "\n".join(parts) or "(no output)"


class CLIToolWrapper:
    """Base class for wrapping CLI tools as A2A agents.

    Subclasses override _build_command() to customize how
    prompts are passed to the tool.
    """

    def __init__(
        self,
        command: str,
        default_args: list[str] | None = None,
        working_dir: str = ".",
        timeout: int = 300,
        environment: dict[str, str] | None = None,
    ):
        self.command = command
        self.default_args = default_args or []
        self.working_dir = working_dir
        self.timeout = timeout
        self.environment = environment or {}

    def _build_command(self, prompt: str) -> list[str]:
        """Build the command to run. Override in subclasses."""
        return [self.command] + self.default_args + [prompt]

    def _build_env(self) -> dict[str, str]:
        """Build environment variables for the subprocess."""
        env = dict(os.environ)
        env.update(self.environment)
        return env

    async def execute(self, prompt: str) -> ToolResult:
        """Run the CLI tool with a prompt and capture output."""
        cmd = self._build_command(prompt)
        logger.info(f"Running: {' '.join(cmd[:3])}...")

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=self.working_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=self._build_env(),
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.timeout,
            )

            result = ToolResult(
                output=stdout.decode(errors="replace"),
                errors=stderr.decode(errors="replace"),
                exit_code=process.returncode or 0,
            )

            # Detect file changes via git
            result.files_changed = await self._detect_file_changes()

            return result

        except asyncio.TimeoutError:
            logger.error(f"Tool timed out after {self.timeout}s")
            return ToolResult(
                errors=f"Timed out after {self.timeout} seconds",
                exit_code=-1,
            )
        except FileNotFoundError:
            logger.error(f"Command not found: {self.command}")
            return ToolResult(
                errors=f"Command not found: {self.command}. Is it installed?",
                exit_code=-1,
            )

    async def execute_streaming(self, prompt: str) -> AsyncGenerator[str, None]:
        """Run tool and stream output line by line."""
        cmd = self._build_command(prompt)

        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=self.working_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=self._build_env(),
        )

        if process.stdout:
            async for line in process.stdout:
                yield line.decode(errors="replace")

        await process.wait()

    async def _detect_file_changes(self) -> list[str]:
        """Detect files changed by the tool using git."""
        try:
            process = await asyncio.create_subprocess_exec(
                "git", "diff", "--name-only",
                cwd=self.working_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await process.communicate()
            lines = stdout.decode().strip().split("\n")
            return [l for l in lines if l.strip()]
        except Exception:
            return []

    async def health_check(self) -> bool:
        """Check if the tool is available."""
        try:
            process = await asyncio.create_subprocess_exec(
                self.command, "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await asyncio.wait_for(process.communicate(), timeout=5)
            return process.returncode == 0
        except Exception:
            return False
