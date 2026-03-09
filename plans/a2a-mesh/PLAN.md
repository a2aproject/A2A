# A2A Mesh: Local Agent Star Network with Web UI

## Vision

A fully local, multi-device agent mesh network where:
- Any OpenAI-compatible LLM (Ollama, vLLM, LM Studio, llama.cpp) powers agents
- External coding tools (Claude Code, Qwen Code, Aider, etc.) can be wrapped as agents
- Star network topology with master/slave configuration
- Agents auto-discover each other on the LAN
- Web UI accessible from any node in the network
- Networked file share so agents can read/write shared workspaces
- Agents operate autonomously after master node reviews and approves their intentions

## Architecture Overview

```
                    ┌─────────────────────────────┐
                    │        Web UI (any node)     │
                    │  Dashboard │ Chat │ Approvals │
                    └──────────────┬──────────────┘
                                   │ HTTP/WS
                    ┌──────────────▼──────────────┐
                    │       MASTER NODE            │
                    │  ┌─────────────────────────┐ │
                    │  │ Orchestrator Agent       │ │
                    │  │ - Intent review/approve  │ │
                    │  │ - Task decomposition     │ │
                    │  │ - Agent assignment        │ │
                    │  │ - Progress monitoring     │ │
                    │  └─────────────────────────┘ │
                    │  ┌─────────────────────────┐ │
                    │  │ Network Services         │ │
                    │  │ - Agent Registry         │ │
                    │  │ - File Share Coordinator │ │
                    │  │ - mDNS Announcer         │ │
                    │  └─────────────────────────┘ │
                    └──┬──────────┬──────────┬────┘
                 A2A   │    A2A   │    A2A   │
            ┌──────────▼┐  ┌─────▼─────┐ ┌──▼─────────┐
            │ SLAVE A   │  │ SLAVE B   │ │ SLAVE C    │
            │           │  │           │ │            │
            │ Ollama    │  │ vLLM      │ │Claude Code │
            │ qwen2.5   │  │ codellama │ │(wrapped)   │
            │           │  │           │ │            │
            │ Role:     │  │ Role:     │ │ Role:      │
            │ Researcher│  │ Coder     │ │ Reviewer   │
            │           │  │           │ │            │
            │ Shared FS │  │ Shared FS │ │ Shared FS  │
            └───────────┘  └───────────┘ └────────────┘
```

## Network Topology: Star Network

```
                    ┌────────┐
          ┌────────►│ MASTER │◄────────┐
          │         └───┬────┘         │
          │  A2A        │ A2A      A2A │
          │             │              │
     ┌────┴───┐    ┌────┴───┐    ┌────┴───┐
     │Slave A │    │Slave B │    │Slave C │
     └────────┘    └────────┘    └────────┘
```

- All agent-to-agent communication routes through the master
- Master has full visibility into all tasks and conversations
- Master can intercept, approve, reject, or redirect any task
- Slaves report status and intentions to master before executing
- Any node can serve the Web UI (reads state from master)

## Implementation Phases

| Phase | Name | Description | Depends On |
|-------|------|-------------|------------|
| 1 | [Core Agent Framework](docs/phase-1-core-agent-framework.md) | OpenAI-compatible A2A agent that works with any local LLM | — |
| 2 | [Star Network & Auto-Discovery](docs/phase-2-star-network-discovery.md) | mDNS discovery, agent registry, star topology | Phase 1 |
| 3 | [Master-Slave Orchestration](docs/phase-3-master-slave-orchestration.md) | Intent review, autonomous execution, task routing | Phase 1, 2 |
| 4 | [Networked File Share](docs/phase-4-networked-file-share.md) | Shared workspace across all nodes | Phase 2 |
| 5 | [Web UI](docs/phase-5-web-ui.md) | Dashboard, chat, approvals — accessible from any node | Phase 1, 2, 3 |
| 6 | [External Tool Integration](docs/phase-6-external-tool-integration.md) | Claude Code, Qwen Code, Aider, etc. as A2A agents | Phase 1 |

## Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Agent runtime | Python 3.11+ | A2A SDK is Python-first |
| A2A protocol | a2a-python SDK | Standard agent communication |
| LLM abstraction | LiteLLM + OpenAI client | Supports 100+ providers with unified API |
| Web framework | FastAPI + Uvicorn | Async, fast, WebSocket support |
| Auto-discovery | Zeroconf (mDNS/DNS-SD) | Zero-config LAN discovery |
| File share | WebDAV over HTTP | Simple, cross-platform, works over LAN |
| Web UI | React + Vite + Tailwind | Fast, modern, lightweight |
| Real-time UI | WebSocket + SSE | Live agent status and chat |
| Config | YAML | Human-readable agent configuration |
| Storage | SQLite | Zero-dependency, embedded |
| Process management | Supervisord or systemd | Agent lifecycle management |

## Directory Structure

```
a2a-mesh/
├── mesh/                          # Python package
│   ├── __init__.py
│   ├── agent/                     # Core agent framework (Phase 1)
│   │   ├── __init__.py
│   │   ├── base.py                # Base OpenAI-compatible agent
│   │   ├── executor.py            # A2A AgentExecutor implementation
│   │   ├── config.py              # YAML config loader
│   │   └── tools.py               # Tool/function calling support
│   ├── network/                   # Network layer (Phase 2)
│   │   ├── __init__.py
│   │   ├── discovery.py           # mDNS auto-discovery
│   │   ├── registry.py            # Agent registry service
│   │   └── topology.py            # Star network manager
│   ├── orchestrator/              # Master-slave (Phase 3)
│   │   ├── __init__.py
│   │   ├── master.py              # Master node orchestrator
│   │   ├── slave.py               # Slave node agent wrapper
│   │   ├── intent.py              # Intent review system
│   │   ├── router.py              # Skill-based task router
│   │   └── autonomy.py            # Autonomous execution engine
│   ├── fileshare/                 # Networked file share (Phase 4)
│   │   ├── __init__.py
│   │   ├── server.py              # WebDAV file server
│   │   ├── client.py              # File share client
│   │   └── sync.py                # File sync manager
│   ├── integrations/              # External tools (Phase 6)
│   │   ├── __init__.py
│   │   ├── claude_code.py         # Claude Code wrapper
│   │   ├── qwen_code.py           # Qwen Code wrapper
│   │   ├── aider.py               # Aider wrapper
│   │   └── generic_cli.py         # Generic CLI tool wrapper
│   ├── ui/                        # Web UI backend (Phase 5)
│   │   ├── __init__.py
│   │   ├── api.py                 # REST API for UI
│   │   └── ws.py                  # WebSocket handlers
│   └── cli.py                     # CLI entry point
├── ui/                            # Web UI frontend (Phase 5)
│   ├── package.json
│   ├── src/
│   │   ├── App.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Chat.tsx
│   │   │   ├── Approvals.tsx
│   │   │   ├── FileExplorer.tsx
│   │   │   └── Settings.tsx
│   │   └── components/
│   └── vite.config.ts
├── configs/                       # Example configurations
│   ├── master.yaml
│   ├── slave-researcher.yaml
│   ├── slave-coder.yaml
│   └── slave-reviewer.yaml
├── pyproject.toml
└── README.md
```

## Configuration Example

### Master Node (`master.yaml`)
```yaml
node:
  role: master
  name: "mesh-master"
  host: "0.0.0.0"
  port: 9000

discovery:
  enabled: true
  method: mdns
  service_type: "_a2a-mesh._tcp.local."

orchestrator:
  auto_approve: false          # Require human approval by default
  auto_approve_skills:         # Auto-approve these skill types
    - "research"
    - "summarize"
  require_approval_skills:     # Always require approval
    - "execute_code"
    - "write_file"
    - "deploy"

fileshare:
  enabled: true
  root: "/shared/workspace"
  port: 9001

ui:
  enabled: true
  port: 8080

llm:
  base_url: "http://localhost:11434/v1"
  model: "llama3.1:70b"
  api_key: "not-needed"
```

### Slave Node (`slave-coder.yaml`)
```yaml
node:
  role: slave
  name: "coder-agent"
  host: "0.0.0.0"
  port: 10001

master:
  discover: true               # Auto-discover master via mDNS
  # url: "http://192.168.1.100:9000"  # Or specify directly

agent:
  name: "Coder"
  description: "Writes, refactors, and debugs code"
  system_prompt: |
    You are an expert software engineer. You write clean,
    well-tested code. You follow best practices and SOLID principles.
    When given a task, you implement it completely and correctly.

skills:
  - id: "write_code"
    name: "Write Code"
    description: "Implement features, write functions, create modules"
    tags: ["code", "implement", "develop"]
  - id: "debug"
    name: "Debug Code"
    description: "Find and fix bugs in code"
    tags: ["debug", "fix", "troubleshoot"]
  - id: "refactor"
    name: "Refactor Code"
    description: "Improve code structure and quality"
    tags: ["refactor", "improve", "clean"]

llm:
  base_url: "http://localhost:8000/v1"   # vLLM
  model: "deepseek-coder-v2"
  api_key: "not-needed"

fileshare:
  mount: "/workspace"          # Local mount point for shared files

integrations:
  claude_code:
    enabled: false
  aider:
    enabled: false
```

## Key Design Decisions

1. **Star over Mesh**: Simpler to reason about, master has full visibility, easier to implement intent review. Can evolve to mesh later.

2. **A2A as the wire protocol**: Don't reinvent comms — use the standard. Agents are opaque to each other, which is correct.

3. **LiteLLM for LLM abstraction**: One interface for Ollama, vLLM, OpenAI, Anthropic, and 100+ others. Swap models by changing config.

4. **WebDAV for file share**: HTTP-based, works across platforms, agents can read/write files naturally. No NFS/SMB complexity.

5. **Intent review before autonomy**: Master sees what agents plan to do before they do it. Critical for safety — especially for code execution and file writes.

6. **UI from any node**: Each node serves a lightweight proxy to the master's state. Open a browser on any device in the network.
