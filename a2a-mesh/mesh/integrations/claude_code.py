"""Claude Code CLI wrapper — exposes Claude Code as an A2A agent."""

from __future__ import annotations

import logging

from mesh.integrations.generic_cli import CLIToolWrapper, ToolResult

logger = logging.getLogger(__name__)


class ClaudeCodeWrapper(CLIToolWrapper):
    """Wraps Claude Code CLI as an A2A agent.

    Uses `claude --print` for non-interactive output.
    Requires ANTHROPIC_API_KEY in environment.
    """

    def __init__(
        self,
        workspace_dir: str = ".",
        api_key: str = "",
        timeout: int = 300,
        model: str = "",
    ):
        env = {}
        if api_key:
            env["ANTHROPIC_API_KEY"] = api_key

        super().__init__(
            command="claude",
            default_args=["--print", "--output-format", "text"],
            working_dir=workspace_dir,
            timeout=timeout,
            environment=env,
        )
        self.model = model

    def _build_command(self, prompt: str) -> list[str]:
        cmd = ["claude", "--print", "--output-format", "text"]
        if self.model:
            cmd.extend(["--model", self.model])
        cmd.append(prompt)
        return cmd

    @staticmethod
    def get_agent_skills() -> list[dict]:
        return [
            {
                "id": "claude_implement",
                "name": "Implement with Claude",
                "description": "Use Claude Code to implement features, fix bugs, refactor code",
                "tags": ["code", "implement", "fix", "refactor", "claude"],
                "input_modes": ["text/plain"],
                "output_modes": ["text/plain"],
            },
            {
                "id": "claude_review",
                "name": "Review with Claude",
                "description": "Use Claude Code to review code and suggest improvements",
                "tags": ["review", "analyze", "claude"],
                "input_modes": ["text/plain"],
                "output_modes": ["text/plain"],
            },
        ]
