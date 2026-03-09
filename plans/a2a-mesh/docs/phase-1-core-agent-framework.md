# Phase 1: Core OpenAI-Compatible Agent Framework

## Goal

Build a reusable A2A agent server that works with **any OpenAI-compatible LLM endpoint** — Ollama, vLLM, LM Studio, llama.cpp, text-generation-webui, or any remote API (OpenAI, Anthropic via LiteLLM, etc.).

One YAML config file. One command to start. Works immediately.

## Deliverables

1. `mesh/agent/config.py` — YAML configuration loader with validation
2. `mesh/agent/base.py` — LLM client abstraction (OpenAI-compatible + LiteLLM fallback)
3. `mesh/agent/executor.py` — A2A `AgentExecutor` wired to the LLM
4. `mesh/agent/tools.py` — Function/tool calling support for capable models
5. `mesh/cli.py` — `mesh start agent --config agent.yaml` CLI
6. Example configs for Ollama, vLLM, and LM Studio

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   A2A Server Layer                    │
│  A2AStarletteApplication + DefaultRequestHandler     │
│  Serves AgentCard at /.well-known/agent-card.json    │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│               MeshAgentExecutor                      │
│  - Receives A2A messages                            │
│  - Converts to OpenAI chat format                   │
│  - Streams responses back as A2A events             │
│  - Manages conversation history per context          │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│               LLMClient                              │
│  - AsyncOpenAI (primary)                            │
│  - LiteLLM fallback for non-OpenAI providers        │
│  - Streaming + non-streaming                        │
│  - Tool/function calling when model supports it     │
└──────────────────────┬──────────────────────────────┘
                       │
              ┌────────▼────────┐
              │  LLM Backend    │
              │  (Ollama/vLLM/  │
              │   LM Studio/    │
              │   OpenAI/etc.)  │
              └─────────────────┘
```

## Detailed Implementation

### 1. Configuration Schema (`mesh/agent/config.py`)

```python
@dataclass
class LLMConfig:
    base_url: str                    # e.g., "http://localhost:11434/v1"
    model: str                       # e.g., "qwen2.5:14b"
    api_key: str = "not-needed"      # Most local servers don't need one
    temperature: float = 0.7
    max_tokens: int = 4096
    supports_tools: bool = False     # Whether model handles function calling
    timeout: int = 120               # Request timeout seconds

@dataclass
class SkillConfig:
    id: str
    name: str
    description: str
    tags: list[str]
    input_modes: list[str] = field(default_factory=lambda: ["text/plain"])
    output_modes: list[str] = field(default_factory=lambda: ["text/plain"])
    examples: list[str] = field(default_factory=list)

@dataclass
class AgentConfig:
    name: str
    description: str
    version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = 10000
    system_prompt: str = "You are a helpful AI agent."
    skills: list[SkillConfig] = field(default_factory=list)
    llm: LLMConfig = None
```

### 2. LLM Client (`mesh/agent/base.py`)

```python
class LLMClient:
    """Unified async client for any OpenAI-compatible endpoint."""

    def __init__(self, config: LLMConfig):
        self.client = AsyncOpenAI(
            base_url=config.base_url,
            api_key=config.api_key,
            timeout=config.timeout,
        )
        self.model = config.model
        self.supports_tools = config.supports_tools

    async def chat(self, messages, tools=None, stream=False):
        """Send chat completion request."""
        kwargs = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
        }
        if tools and self.supports_tools:
            kwargs["tools"] = tools
        return await self.client.chat.completions.create(**kwargs)

    async def chat_stream(self, messages, tools=None):
        """Yield streaming chunks."""
        response = await self.chat(messages, tools, stream=True)
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
```

### 3. A2A Executor (`mesh/agent/executor.py`)

The executor bridges A2A protocol ↔ OpenAI chat completions:

```python
class MeshAgentExecutor(AgentExecutor):
    """A2A executor backed by an OpenAI-compatible LLM."""

    def __init__(self, llm: LLMClient, system_prompt: str):
        self.llm = llm
        self.system_prompt = system_prompt
        self.conversations: dict[str, list] = {}  # context_id → messages

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        # 1. Extract user message from A2A request
        user_text = self._extract_text(context)
        context_id = context.context_id or "default"

        # 2. Build conversation history
        if context_id not in self.conversations:
            self.conversations[context_id] = [
                {"role": "system", "content": self.system_prompt}
            ]
        self.conversations[context_id].append(
            {"role": "user", "content": user_text}
        )

        # 3. Stream LLM response
        full_response = ""
        async for chunk in self.llm.chat_stream(self.conversations[context_id]):
            full_response += chunk
            # Send streaming status update
            await event_queue.enqueue_status_update(
                state="working",
                message=chunk
            )

        # 4. Store assistant response in history
        self.conversations[context_id].append(
            {"role": "assistant", "content": full_response}
        )

        # 5. Send final artifact and completion
        await event_queue.enqueue_artifact(text=full_response)
        await event_queue.enqueue_status_update(state="completed")

    async def cancel(self, context, event_queue):
        await event_queue.enqueue_status_update(state="canceled")
```

### 4. Tool/Function Calling (`mesh/agent/tools.py`)

For models that support function calling (GPT-4, Qwen2.5, Mistral, etc.):

```python
class ToolRegistry:
    """Register and execute tools for agents."""

    def __init__(self):
        self.tools: dict[str, Callable] = {}
        self.schemas: list[dict] = []

    def register(self, name, description, parameters, handler):
        self.tools[name] = handler
        self.schemas.append({
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters,
            }
        })

    async def execute(self, name, arguments):
        handler = self.tools[name]
        if asyncio.iscoroutinefunction(handler):
            return await handler(**arguments)
        return handler(**arguments)
```

**Built-in tools provided:**
- `read_file` — Read file from shared workspace
- `write_file` — Write file to shared workspace
- `list_files` — List files in shared workspace
- `execute_command` — Run shell command (requires master approval)
- `search_web` — Web search (when available)
- `delegate_task` — Ask another agent for help (via A2A)

### 5. CLI Entry Point (`mesh/cli.py`)

```bash
# Start an agent from config
mesh start --config configs/slave-coder.yaml

# Start master node
mesh start --config configs/master.yaml

# List discovered agents
mesh agents list

# Send a message to an agent
mesh send "coder-agent" "Write a Python function to parse CSV files"

# Check agent status
mesh status
```

## Configuration Examples

### Ollama Backend
```yaml
agent:
  name: "research-agent"
  description: "Researches topics thoroughly"
  port: 10001
  system_prompt: "You are a research specialist..."
llm:
  base_url: "http://localhost:11434/v1"
  model: "qwen2.5:14b"
  supports_tools: true
skills:
  - id: research
    name: "Research"
    description: "Deep research on any topic"
    tags: [research, analyze, summarize]
```

### vLLM Backend
```yaml
agent:
  name: "coder-agent"
  description: "Expert software engineer"
  port: 10002
  system_prompt: "You are an expert coder..."
llm:
  base_url: "http://gpu-server:8000/v1"
  model: "deepseek-coder-v2"
  max_tokens: 8192
  supports_tools: false
skills:
  - id: write_code
    name: "Write Code"
    description: "Implement features and write code"
    tags: [code, implement, develop]
```

### LM Studio Backend
```yaml
agent:
  name: "reviewer-agent"
  description: "Code review specialist"
  port: 10003
llm:
  base_url: "http://localhost:1234/v1"
  model: "lmstudio-community/Meta-Llama-3-8B"
  supports_tools: false
skills:
  - id: review
    name: "Code Review"
    description: "Review code for bugs and best practices"
    tags: [review, quality, bugs]
```

## Testing Plan

1. **Unit tests**: Config loading, message conversion, tool registry
2. **Integration test with Ollama**: Start agent → send message → get response
3. **Integration test with mock OpenAI**: Verify protocol compliance without real LLM
4. **Streaming test**: Verify SSE streaming works end-to-end
5. **Multi-turn test**: Verify conversation history is maintained across turns
6. **Tool calling test**: Verify function calling with capable models

## Success Criteria

- [ ] `mesh start --config agent.yaml` starts an A2A agent in < 3 seconds
- [ ] Agent responds to A2A `message/send` requests correctly
- [ ] Agent streams responses via `message/stream` SSE
- [ ] Agent maintains conversation history per context
- [ ] Works with Ollama, vLLM, and LM Studio without code changes
- [ ] Config-only setup — no Python code needed to create a new agent
