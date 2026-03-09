"""Aider CLI wrapper — exposes Aider as an A2A agent."""

from __future__ import annotations

import logging

from mesh.integrations.generic_cli import CLIToolWrapper

logger = logging.getLogger(__name__)


class AiderWrapper(CLIToolWrapper):
    """Wraps Aider as an A2A agent.

    Aider is a CLI coding assistant that can use any OpenAI-compatible LLM.
    This wrapper runs it in non-interactive mode with --message.
    """

    def __init__(
        self,
        workspace_dir: str = ".",
        llm_base_url: str = "",
        llm_api_key: str = "not-needed",
        llm_model: str = "",
        timeout: int = 300,
        files_to_edit: list[str] | None = None,
    ):
        env = {}
        if llm_base_url:
            env["OPENAI_API_BASE"] = llm_base_url
        if llm_api_key:
            env["OPENAI_API_KEY"] = llm_api_key

        super().__init__(
            command="aider",
            default_args=[
                "--no-auto-commits",
                "--no-git",
                "--yes-always",
            ],
            working_dir=workspace_dir,
            timeout=timeout,
            environment=env,
        )
        self.llm_model = llm_model
        self.files_to_edit = files_to_edit or []

    def _build_command(self, prompt: str) -> list[str]:
        cmd = [
            "aider",
            "--no-auto-commits",
            "--no-git",
            "--yes-always",
            "--message", prompt,
        ]
        if self.llm_model:
            cmd.extend(["--model", self.llm_model])
        if self.files_to_edit:
            cmd.extend(self.files_to_edit)
        return cmd

    @staticmethod
    def get_agent_skills() -> list[dict]:
        return [
            {
                "id": "aider_edit",
                "name": "Edit Code with Aider",
                "description": "Make targeted code edits using Aider",
                "tags": ["code", "edit", "refactor", "aider"],
                "input_modes": ["text/plain"],
                "output_modes": ["text/plain"],
            },
        ]
