# Research: OpenAI-Compatible Local Agent Mesh with UI

## Question

> Does A2A work with any OpenAI-compatible framework such as Ollama, vLLM, Claude Code, Qwen Code? If not, how hard would it be to make it work with all of them? And is there a user UI?

## Executive Summary

**A2A is LLM-agnostic by design** — it's a communication protocol between agents, not an LLM wrapper. Any agent can use any LLM internally (Ollama, vLLM, Qwen, etc.) and expose itself as an A2A server. However, there are **no turnkey templates** for OpenAI-compatible backends and **no user-facing UI** exists in the project.

Building a local multi-device agent mesh with easy role assignment, OpenAI-compatible LLM support, and a web UI is feasible but requires new components.

---

## Current State Analysis

### What A2A Provides Today

| Component | Status | Details |
|-----------|--------|---------|
| Agent-to-agent protocol | Complete | JSON-RPC 2.0 over HTTP(S), streaming via SSE |
| Agent discovery | Complete | Agent Cards at `/.well-known/agent-card.json` |
| Python SDK | Complete | `a2a-python` package with server/client |
| JS/TS SDK | Complete | `a2a-js` package |
| Go SDK | Complete | `a2a-go` package |
| Multi-turn conversations | Complete | Via `taskId` and `contextId` |
| Streaming | Complete | Server-Sent Events (SSE) |
| Task management | Complete | Stateful tasks with lifecycle |
| Authentication | Complete | OAuth2, API keys, mTLS |

### What's Missing for the Local Mesh Vision

| Component | Status | Effort |
|-----------|--------|--------|
| OpenAI-compatible agent template | Missing | 1-2 days |
| Web UI (dashboard + chat) | Missing | 3-5 days |
| LAN agent discovery/registry | Missing | 2-3 days |
| Role assignment system | Missing | 2-3 days |
| Orchestrator/router agent | Missing | 5-7 days |

### OpenAI-Compatible Framework Compatibility

| Framework | Type | OpenAI-Compatible API | Can Power A2A Agent? |
|-----------|------|----------------------|---------------------|
| **Ollama** | Local LLM server | Yes (`/v1/chat/completions`) | Yes — via OpenAI client or LangChain |
| **vLLM** | GPU inference server | Yes (`/v1/chat/completions`) | Yes — via OpenAI client or LangChain |
| **Qwen (via Ollama/vLLM)** | Model family | Yes (when served via Ollama/vLLM) | Yes |
| **LM Studio** | Local LLM desktop app | Yes (`/v1/chat/completions`) | Yes |
| **llama.cpp server** | Lightweight inference | Yes (`/v1/chat/completions`) | Yes |
| **Claude Code** | CLI dev tool | No (not an LLM server) | No — different concept entirely |
| **text-generation-webui** | Web-based inference | Yes (with API extension) | Yes |

**Note on Claude Code:** Claude Code is Anthropic's CLI tool for software development — it's not an LLM serving framework. It cannot be used as a backend LLM provider. However, Claude models can be accessed via the Anthropic API and used to power A2A agents.

---

## Proposed Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Web UI (new)                          │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────────┐  │
│  │ Agent       │ │ Chat         │ │ Task Flow        │  │
│  │ Dashboard   │ │ Interface    │ │ Visualizer       │  │
│  └─────────────┘ └──────────────┘ └──────────────────┘  │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP/WebSocket
┌──────────────────────▼──────────────────────────────────┐
│              Orchestrator Agent (new)                     │
│  ┌──────────────┐ ┌─────────────┐ ┌──────────────────┐  │
│  │ Agent        │ │ Skill-based │ │ Task             │  │
│  │ Registry     │ │ Router      │ │ Coordinator      │  │
│  └──────────────┘ └─────────────┘ └──────────────────┘  │
└──────┬───────────────┬──────────────┬───────────────────┘
       │ A2A           │ A2A          │ A2A
┌──────▼─────┐  ┌──────▼─────┐ ┌─────▼──────┐
│ Agent 1    │  │ Agent 2    │ │ Agent 3    │
│ Role:      │  │ Role:      │ │ Role:      │
│ Researcher │  │ Coder      │ │ Reviewer   │
│            │  │            │ │            │
│ LLM:      │  │ LLM:       │ │ LLM:       │
│ Ollama     │  │ vLLM       │ │ Ollama     │
│ (qwen2.5)  │  │ (codellama)│ │ (llama3)  │
│            │  │            │ │            │
│ Device A   │  │ Device B   │ │ Device C   │
│ :10001     │  │ :10002     │ │ :10003     │
└────────────┘  └────────────┘ └────────────┘
```

### Component Details

#### 1. OpenAI-Compatible Agent Template

A reusable A2A agent server that accepts any OpenAI-compatible endpoint as its LLM backend.

**Configuration (YAML):**
```yaml
agent:
  name: "research-agent"
  role: "researcher"
  description: "Researches topics and summarizes findings"
  port: 10001

llm:
  base_url: "http://localhost:11434/v1"  # Ollama
  model: "qwen2.5:14b"
  api_key: "not-needed"  # Ollama doesn't require one

skills:
  - id: "research"
    name: "Research Topic"
    description: "Research a topic and provide a summary"
    input_modes: ["text/plain"]
    output_modes: ["text/plain"]

system_prompt: |
  You are a research agent. When given a topic, you thoroughly
  research it and provide a well-structured summary.

orchestrator:
  registry_url: "http://192.168.1.100:9000"  # Where to register
```

**Minimal Python implementation (~150 lines):**
```python
# openai_agent.py — conceptual skeleton
from openai import AsyncOpenAI
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import AgentCard, AgentSkill

class OpenAICompatibleAgent:
    """Agent powered by any OpenAI-compatible API (Ollama, vLLM, etc.)."""

    def __init__(self, config: dict):
        self.client = AsyncOpenAI(
            base_url=config["llm"]["base_url"],
            api_key=config["llm"].get("api_key", "not-needed"),
        )
        self.model = config["llm"]["model"]
        self.system_prompt = config.get("system_prompt", "You are a helpful agent.")

    async def invoke(self, messages: list[dict]) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": self.system_prompt}] + messages,
            stream=False,
        )
        return response.choices[0].message.content

class OpenAIAgentExecutor(AgentExecutor):
    """A2A executor that delegates to an OpenAI-compatible backend."""

    def __init__(self, agent: OpenAICompatibleAgent):
        self.agent = agent

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        # Extract user message from A2A request
        user_message = context.get_user_message()
        # Call OpenAI-compatible LLM
        result = await self.agent.invoke([{"role": "user", "content": user_message}])
        # Send result back via A2A
        await event_queue.enqueue_artifact(text=result)
        await event_queue.enqueue_status_update(state="completed")

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
```

#### 2. Agent Registry Service

Lightweight HTTP service for LAN agent discovery.

**API:**
```
POST   /agents/register    — Agent registers itself (sends Agent Card)
DELETE /agents/{agent_id}   — Agent deregisters on shutdown
GET    /agents              — List all registered agents
GET    /agents?skill=code   — Find agents by skill
GET    /agents/{agent_id}   — Get specific agent card
```

**Features:**
- Heartbeat-based health checking (agents ping every 30s)
- Auto-deregister dead agents
- Simple SQLite or in-memory storage
- Optional mDNS announcement for zero-config discovery

#### 3. Web UI

**Tech stack recommendation:** React + Vite + Tailwind (or Svelte for lighter weight)

**Pages:**
1. **Dashboard** — Grid of agent cards showing name, role, status, device, LLM model
2. **Chat** — Send messages to any agent or the orchestrator; see streaming responses
3. **Roles** — Define role templates (researcher, coder, reviewer, etc.) with system prompts and skill definitions
4. **Task Flow** — Visualize agent-to-agent task delegation in real-time
5. **Config** — Add/edit agent configurations, LLM endpoints

#### 4. Orchestrator Agent

A special A2A agent that:
- Maintains the agent registry
- Routes incoming tasks to the best-suited agent based on skills
- Coordinates multi-agent workflows (e.g., "research → code → review")
- Reports progress back to the UI

---

## Implementation Plan

### Phase 1: OpenAI-Compatible Agent Template (Week 1)
1. Create `openai-compatible-agent/` with YAML config + Python server
2. Test with Ollama (`llama3`, `qwen2.5`, `codellama`)
3. Test with vLLM serving various models
4. Test with LM Studio
5. Write a simple test client

### Phase 2: Agent Registry + LAN Discovery (Week 1-2)
1. Build registry service (FastAPI + SQLite)
2. Add agent self-registration on startup
3. Add heartbeat / health checking
4. Add skill-based query API
5. Optional: mDNS for zero-config

### Phase 3: Web UI MVP (Week 2-3)
1. Agent dashboard (list agents, status, roles)
2. Chat interface (talk to any agent, streaming)
3. Role management (create/edit role templates)
4. Agent spawning (start new agents from UI)

### Phase 4: Orchestrator Agent (Week 3-4)
1. Skill-based task routing
2. Multi-agent workflow chains
3. Task flow visualization in UI
4. Error handling and retry logic

---

## Effort Estimate

| Phase | Component | Effort | Dependencies |
|-------|-----------|--------|-------------|
| 1 | OpenAI-compatible agent template | 1-2 days | A2A Python SDK |
| 2 | Agent registry service | 2-3 days | Phase 1 |
| 3 | Web UI MVP | 3-5 days | Phase 2 |
| 4 | Orchestrator agent | 5-7 days | Phase 2 |
| **Total** | **Full MVP** | **~2-3 weeks** | |

## Alternative Approaches Considered

### Use Existing Multi-Agent Frameworks
Frameworks like CrewAI, AutoGen, or LangGraph already support multi-agent patterns. However:
- They don't work across devices/networks natively
- They're tightly coupled (agents share memory/state)
- A2A provides true decoupled agent-to-agent communication

### Use MCP Instead of A2A
MCP (Model Context Protocol) is for agent-to-tool communication, not agent-to-agent. A2A is the right protocol for this use case. They're complementary — agents can use MCP internally for tools while communicating via A2A.

### Build From Scratch Without A2A
Possible but wasteful. A2A already solves:
- Agent discovery (Agent Cards)
- Communication protocol (JSON-RPC)
- Streaming (SSE)
- Task lifecycle management
- Multi-turn conversations
- Authentication

---

## Key Risks

1. **Local LLM quality** — Smaller models may struggle with complex agent instructions and role-following
2. **Network latency** — Cross-device communication adds latency vs. in-process agents
3. **Context management** — Long multi-agent conversations may exceed local model context windows
4. **No function calling** — Some local models don't support tool/function calling well, limiting agent capabilities

## Recommendations

1. **Start with Phase 1** — Get a single Ollama-powered agent running with A2A in 1-2 days
2. **Use LiteLLM as the abstraction layer** — It supports 100+ LLM providers with a unified OpenAI-compatible interface
3. **Keep the UI simple initially** — A Streamlit or Gradio prototype could be built in hours before investing in a full React app
4. **Test with capable models** — Use at least 7B+ parameter models for reliable agent behavior
