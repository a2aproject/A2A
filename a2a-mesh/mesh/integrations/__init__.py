"""External tool integrations — wrap CLI tools as A2A agents."""

from mesh.integrations.generic_cli import CLIToolWrapper
from mesh.integrations.claude_code import ClaudeCodeWrapper
from mesh.integrations.aider import AiderWrapper

__all__ = ["CLIToolWrapper", "ClaudeCodeWrapper", "AiderWrapper"]
