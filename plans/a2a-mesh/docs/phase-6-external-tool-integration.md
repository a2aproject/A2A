# Phase 6: External Tool Integration (Claude Code, Qwen Code, etc.)

## Goal

Wrap external coding tools — Claude Code, Qwen Code, Aider, Cursor, Continue, etc. — as A2A agents. They appear as regular agents in the mesh, receive tasks, and report results through the standard A2A protocol.

## Deliverables

1. `mesh/integrations/generic_cli.py` — Generic CLI tool wrapper (base class)
2. `mesh/integrations/claude_code.py` — Claude Code specific wrapper
3. `mesh/integrations/qwen_code.py` — Qwen Code specific wrapper
4. `mesh/integrations/aider.py` — Aider specific wrapper
5. `mesh/integrations/subprocess_agent.py` — Subprocess management for CLI tools

## Architecture

```
┌──────────────────────────────────────────┐
│           A2A Agent Server               │
│  (standard A2A protocol to mesh)         │
├──────────────────────────────────────────┤
│        Tool Integration Layer            │
│  - Converts A2A messages to CLI input    │
│  - Captures CLI output as A2A responses  │
│  - Manages tool subprocess lifecycle     │
├──────────────────────────────────────────┤
│        External Tool (subprocess)        │
│  claude code / qwen code / aider / etc.  │
│  Running in project directory            │
└──────────────────────────────────────────┘
```

## How Each Tool Is Wrapped

### Strategy: Subprocess + stdin/stdout Piping

Most coding tools are CLI-based. We:
1. Launch the tool as a subprocess pointing at the shared workspace
2. Pipe A2A task messages into the tool's stdin (or via CLI args)
3. Capture stdout/stderr as the agent's response
4. Report file changes back through A2A

### Alternative Strategy: API-Based (where available)

Some tools expose APIs:
- Claude Code: Can be invoked via `claude` CLI with `--print` flag for non-interactive use
- Aider: Has a Python API (`aider.coders`)
- LM Studio: HTTP API

## Implementation

### Generic CLI Wrapper (`mesh/integrations/generic_cli.py`)

```python
class CLIToolWrapper:
    """Base class for wrapping CLI coding tools as A2A agents."""

    def __init__(self, config: CLIToolConfig):
        self.command = config.command       # e.g., "claude"
        self.args = config.default_args     # e.g., ["--print"]
        self.working_dir = config.working_dir
        self.env = config.environment       # Extra env vars
        self.timeout = config.timeout       # Max execution time

    async def execute(self, prompt: str) -> ToolResult:
        """Run the CLI tool with a prompt and capture output."""
        cmd = [self.command] + self.args + [prompt]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=self.working_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={**os.environ, **self.env}
        )

        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=self.timeout
        )

        return ToolResult(
            output=stdout.decode(),
            errors=stderr.decode(),
            exit_code=process.returncode,
            files_changed=await self._detect_file_changes()
        )

    async def execute_streaming(self, prompt: str) -> AsyncGenerator[str, None]:
        """Run tool and stream output line by line."""
        process = await asyncio.create_subprocess_exec(
            *[self.command] + self.args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.working_dir,
        )

        process.stdin.write(prompt.encode() + b"\n")
        await process.stdin.drain()

        async for line in process.stdout:
            yield line.decode()

    async def _detect_file_changes(self) -> list[FileChange]:
        """Detect what files the tool modified (via git diff or inotify)."""
        # Use git diff if in a git repo
        result = await asyncio.create_subprocess_exec(
            "git", "diff", "--name-status", "HEAD",
            cwd=self.working_dir,
            stdout=asyncio.subprocess.PIPE
        )
        stdout, _ = await result.communicate()
        return self._parse_git_diff(stdout.decode())
```

### Claude Code Wrapper (`mesh/integrations/claude_code.py`)

```python
class ClaudeCodeWrapper(CLIToolWrapper):
    """Wraps Claude Code CLI as an A2A agent."""

    def __init__(self, config):
        super().__init__(CLIToolConfig(
            command="claude",
            default_args=["--print", "--output-format", "text"],
            working_dir=config.workspace_dir,
            timeout=300,  # 5 min max
            environment={
                "ANTHROPIC_API_KEY": config.api_key,
            }
        ))

    async def execute(self, prompt: str) -> ToolResult:
        """Execute Claude Code with a prompt."""
        # Claude Code supports --print for non-interactive output
        cmd = ["claude", "--print", "--output-format", "text", prompt]
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=self.working_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={**os.environ, **self.env}
        )
        stdout, stderr = await asyncio.wait_for(
            process.communicate(), timeout=self.timeout
        )
        return ToolResult(
            output=stdout.decode(),
            errors=stderr.decode(),
            exit_code=process.returncode,
            files_changed=await self._detect_file_changes()
        )

    def get_agent_skills(self) -> list[dict]:
        return [
            {
                "id": "claude_code_implement",
                "name": "Implement with Claude Code",
                "description": "Use Claude Code to implement features, fix bugs, refactor code",
                "tags": ["code", "implement", "fix", "refactor", "claude"],
            },
            {
                "id": "claude_code_review",
                "name": "Review with Claude Code",
                "description": "Use Claude Code to review code and suggest improvements",
                "tags": ["review", "analyze", "claude"],
            }
        ]
```

**Claude Code Configuration:**
```yaml
agent:
  name: "claude-code-agent"
  description: "Powered by Claude Code CLI"
  port: 10004
integration:
  type: "claude_code"
  api_key: "${ANTHROPIC_API_KEY}"
  workspace_dir: "/workspace"
  timeout: 300
  args: ["--print", "--output-format", "text"]
skills:
  - id: implement
    name: "Implement Feature"
    description: "Full feature implementation using Claude"
    tags: [code, implement, feature]
  - id: fix
    name: "Fix Bug"
    description: "Debug and fix issues in code"
    tags: [fix, debug, bug]
```

### Qwen Code Wrapper (`mesh/integrations/qwen_code.py`)

```python
class QwenCodeWrapper(CLIToolWrapper):
    """Wraps Qwen Code / Qwen Agent as an A2A agent.

    Qwen Code can run via:
    1. Ollama serving qwen2.5-coder → use OpenAI-compatible agent (Phase 1)
    2. Qwen-Agent CLI tool → use this wrapper
    3. Direct API → use OpenAI-compatible agent with base_url
    """

    def __init__(self, config):
        # If using Qwen via Ollama, delegate to OpenAI-compatible agent
        if config.get("use_ollama"):
            self.mode = "ollama"
            self.llm_config = {
                "base_url": config.get("ollama_url", "http://localhost:11434/v1"),
                "model": config.get("model", "qwen2.5-coder:14b"),
            }
        else:
            # Qwen-Agent CLI mode
            super().__init__(CLIToolConfig(
                command="qwen-agent",
                default_args=["--non-interactive"],
                working_dir=config.workspace_dir,
                timeout=300,
            ))
            self.mode = "cli"
```

**Qwen Configuration (Ollama mode — recommended):**
```yaml
agent:
  name: "qwen-coder"
  description: "Qwen 2.5 Coder via Ollama"
  port: 10005
llm:
  base_url: "http://localhost:11434/v1"
  model: "qwen2.5-coder:14b"
  supports_tools: true
skills:
  - id: code
    name: "Write Code"
    description: "Expert Python/JS/Rust code generation"
    tags: [code, implement]
```

### Aider Wrapper (`mesh/integrations/aider.py`)

```python
class AiderWrapper(CLIToolWrapper):
    """Wraps Aider as an A2A agent."""

    def __init__(self, config):
        super().__init__(CLIToolConfig(
            command="aider",
            default_args=[
                "--no-auto-commits",
                "--no-git",
                "--yes-always",          # Don't ask for confirmation
                "--message",             # Will be followed by the prompt
            ],
            working_dir=config.workspace_dir,
            timeout=300,
            environment={
                "OPENAI_API_BASE": config.get("llm_base_url", ""),
                "OPENAI_API_KEY": config.get("llm_api_key", "not-needed"),
            }
        ))

    async def execute(self, prompt: str) -> ToolResult:
        """Run aider with a specific task."""
        cmd = [
            "aider",
            "--no-auto-commits",
            "--no-git",
            "--yes-always",
            "--message", prompt,
        ]
        # Add files to edit if specified
        if self.files_to_edit:
            cmd.extend(self.files_to_edit)
        return await self._run(cmd)
```

**Aider Configuration:**
```yaml
agent:
  name: "aider-agent"
  description: "Aider-powered code editor"
  port: 10006
integration:
  type: "aider"
  workspace_dir: "/workspace"
  llm_base_url: "http://localhost:11434"  # Use with Ollama
  llm_model: "qwen2.5-coder:14b"
skills:
  - id: edit_code
    name: "Edit Code"
    description: "Make targeted code edits with Aider"
    tags: [edit, refactor, code]
```

### Subprocess Agent (`mesh/integrations/subprocess_agent.py`)

Manages the lifecycle of external tool processes:

```python
class SubprocessAgent:
    """Manages external tool as a long-running subprocess."""

    def __init__(self, wrapper: CLIToolWrapper):
        self.wrapper = wrapper
        self.process = None

    async def start(self):
        """Start the external tool process."""
        self.process = await asyncio.create_subprocess_exec(...)

    async def send_task(self, task_text: str) -> str:
        """Send a task and collect the response."""

    async def stop(self):
        """Gracefully stop the external tool."""
        if self.process:
            self.process.terminate()
            await self.process.wait()

    async def health_check(self) -> bool:
        """Check if the subprocess is still running."""
        return self.process and self.process.returncode is None
```

## Integration Matrix

| Tool | Mode | Local LLM | Cloud LLM | Streaming | File Detection |
|------|------|-----------|-----------|-----------|----------------|
| **Claude Code** | CLI subprocess | No (cloud only) | Yes (Anthropic) | Yes (stdout) | git diff |
| **Qwen Code** | Ollama/CLI | Yes (Ollama) | Yes (Dashscope) | Yes | git diff |
| **Aider** | CLI subprocess | Yes (any OpenAI-compat) | Yes (OpenAI/Anthropic) | Yes (stdout) | git diff |
| **Continue** | LSP/CLI | Yes (Ollama) | Yes (various) | Limited | git diff |
| **Cursor** | Not wrappable | — | — | — | — |
| **Custom CLI** | Generic wrapper | Depends | Depends | Yes (stdout) | git diff |

## Security Considerations

- **API keys**: Stored in environment variables, never in config files
- **Subprocess isolation**: Tools run in workspace directory only
- **Command injection**: All prompts sanitized before passing to CLI
- **File access**: Tools confined to workspace via chroot or path validation
- **Network access**: Tools may need internet for cloud LLM APIs

## Testing Plan

1. **Claude Code**: Send prompt → get code output → verify file changes
2. **Qwen (Ollama)**: Standard OpenAI-compatible test (Phase 1 covers this)
3. **Aider**: Send edit request → verify file modified correctly
4. **Generic wrapper**: Custom CLI tool wrapped and responding
5. **Error handling**: Tool crashes, timeouts, invalid output
6. **File change detection**: Verify git diff parsing works

## Success Criteria

- [ ] Claude Code wrapped as A2A agent, receives tasks, returns code
- [ ] Qwen models accessible via Ollama as standard agents
- [ ] Aider wrapped as A2A agent for targeted code editing
- [ ] Generic CLI wrapper supports arbitrary tools with minimal config
- [ ] All wrapped tools report file changes back to master
- [ ] Tools appear as normal agents in the mesh UI
- [ ] Failure/timeout in external tools handled gracefully
