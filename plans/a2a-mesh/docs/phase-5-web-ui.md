# Phase 5: Web UI (Accessible From Any Node)

## Goal

A web dashboard accessible from any device on the network. Open a browser, go to any node's IP, get full visibility and control over the entire mesh.

## Deliverables

1. `mesh/ui/api.py` — REST API backend for the UI
2. `mesh/ui/ws.py` — WebSocket server for real-time updates
3. `ui/` — React + Vite + Tailwind frontend
4. UI proxy on each node so `http://<any-node>:8080` works

## Key Pages

### 1. Dashboard
```
┌─────────────────────────────────────────────────────────┐
│  A2A Mesh Dashboard                    [⚙ Settings]     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Cluster Status: ● Online (4 nodes)                     │
│                                                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │ ★ Master    │ │ Researcher  │ │ Coder       │       │
│  │ llama3:70b  │ │ qwen2.5:14b │ │ codellama   │       │
│  │ ● Online    │ │ ● Online    │ │ ● Online    │       │
│  │ Tasks: 0    │ │ Tasks: 1    │ │ Tasks: 0    │       │
│  │ 192.168.1.1 │ │ 192.168.1.2 │ │ 192.168.1.3 │       │
│  └─────────────┘ └─────────────┘ └─────────────┘       │
│                                                         │
│  ┌─────────────┐                                        │
│  │ Reviewer    │                                        │
│  │ claude-code │                                        │
│  │ ● Online    │                                        │
│  │ Tasks: 0    │                                        │
│  │ 192.168.1.4 │                                        │
│  └─────────────┘                                        │
│                                                         │
│  Recent Activity                                        │
│  ┌─────────────────────────────────────────────────┐    │
│  │ 10:31 Researcher → completed "API research"     │    │
│  │ 10:30 Master → assigned task to Researcher      │    │
│  │ 10:29 Coder → registered on network             │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### 2. Chat Interface
```
┌─────────────────────────────────────────────────────────┐
│  Chat                        [To: All Agents ▼]         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  You: Build a REST API for user management              │
│                                                         │
│  ★ Master: I'll break this down:                        │
│    1. Research → Researcher agent                       │
│    2. Implementation → Coder agent                      │
│    3. Review → Reviewer agent                           │
│                                                         │
│  ⚠ INTENT REVIEW                                       │
│  Coder wants to: Create 4 files in src/api/             │
│  Risk: medium                                           │
│  [✅ Approve] [❌ Reject] [✏ Modify]                    │
│                                                         │
│  Researcher: Here's my analysis of REST API best...     │
│    ├─ Authentication: JWT recommended                   │
│    ├─ Endpoints: CRUD + search                          │
│    └─ [View full report]                                │
│                                                         │
│  Coder: ● Working on implementation...                  │
│    ├─ ✅ Created src/api/models.py                      │
│    ├─ ✅ Created src/api/routes.py                      │
│    ├─ ● Writing src/api/auth.py...                      │
│    └─ ○ Pending: src/api/tests.py                       │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  [Type a message...]                          [Send ▶]  │
└─────────────────────────────────────────────────────────┘
```

### 3. Intent Approvals Queue
```
┌─────────────────────────────────────────────────────────┐
│  Pending Approvals (2)                                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │ Coder Agent → write_code                        │    │
│  │ "Create user authentication module"              │    │
│  │ Files: src/auth.py, src/middleware.py            │    │
│  │ Risk: medium │ Time: 2 min ago                  │    │
│  │ [✅ Approve] [❌ Reject] [📝 Details]            │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │ Coder Agent → execute_command                   │    │
│  │ "Run: pip install pyjwt bcrypt"                  │    │
│  │ Risk: high                                       │    │
│  │ [✅ Approve] [❌ Reject] [📝 Details]            │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  History                                                │
│  ✅ Researcher → research (auto-approved)               │
│  ✅ Coder → read_file (auto-approved)                   │
│  ✅ Coder → write_code (master-approved)                │
└─────────────────────────────────────────────────────────┘
```

### 4. File Explorer
```
┌─────────────────────────────────────────────────────────┐
│  Shared Workspace          [🔍 Search] [📁 New Folder]  │
├────────────────────┬────────────────────────────────────┤
│                    │                                    │
│  📁 src/           │  src/api/routes.py                 │
│    📁 api/         │  Modified by: coder-agent          │
│      📄 models.py  │  Modified: 2 min ago               │
│      📄 routes.py ◄│                                    │
│      📄 auth.py    │  ```python                         │
│    📁 utils/       │  from fastapi import APIRouter      │
│  📁 docs/          │  from .models import User           │
│  📁 tests/         │                                    │
│  📄 README.md      │  router = APIRouter()               │
│                    │  ...                                │
│                    │  ```                                │
│                    │                                    │
│                    │  [📥 Download] [✏ Edit] [📋 Copy]  │
└────────────────────┴────────────────────────────────────┘
```

### 5. Settings / Agent Configuration
```
┌─────────────────────────────────────────────────────────┐
│  Settings                                               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Node Configuration                                     │
│  ┌─────────────────────────────────────────────────┐    │
│  │ Role: [Master ▼]                                │    │
│  │ Name: [mesh-master         ]                    │    │
│  │ Port: [9000                ]                    │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  Autonomy Level                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │ ○ Manual    — Approve everything                │    │
│  │ ● Supervised — Auto-approve low risk            │    │
│  │ ○ Autonomous — Auto-approve except critical     │    │
│  │ ○ Full Auto — No approvals needed               │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  Agent Roles                                            │
│  [+ Add Role]                                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │ Researcher │ Coder │ Reviewer │ + Custom        │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  LLM Endpoints                                          │
│  [+ Add Endpoint]                                       │
│  ┌─────────────────────────────────────────────────┐    │
│  │ Ollama    http://localhost:11434/v1    ● Online  │    │
│  │ vLLM      http://gpu-box:8000/v1      ● Online  │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## Implementation

### Backend API (`mesh/ui/api.py`)

```python
# FastAPI routes for UI backend
router = APIRouter(prefix="/api")

# Dashboard
@router.get("/cluster/status")
@router.get("/agents")
@router.get("/agents/{agent_id}")
@router.get("/activity/recent")

# Chat
@router.post("/chat/send")          # Send message to agent/orchestrator
@router.get("/chat/history")        # Get chat history

# Approvals
@router.get("/approvals/pending")
@router.post("/approvals/{intent_id}/approve")
@router.post("/approvals/{intent_id}/reject")
@router.get("/approvals/history")

# Files
@router.get("/files/tree")
@router.get("/files/{path:path}")
@router.put("/files/{path:path}")
@router.get("/files/search")

# Settings
@router.get("/settings")
@router.put("/settings")
@router.get("/settings/roles")
@router.post("/settings/roles")
```

### WebSocket for Real-Time Updates (`mesh/ui/ws.py`)

```python
@router.websocket("/ws")
async def websocket_handler(ws: WebSocket):
    await ws.accept()
    # Subscribe to all mesh events
    async for event in mesh_event_bus.subscribe():
        await ws.send_json({
            "type": event.type,    # "agent_status", "task_update", "intent_pending", etc.
            "data": event.data,
            "timestamp": event.timestamp
        })
```

**Event types pushed to UI:**
- `agent_joined` / `agent_left` — Node topology changes
- `task_created` / `task_updated` / `task_completed` — Task lifecycle
- `intent_pending` / `intent_approved` / `intent_rejected` — Approval flow
- `file_changed` — Workspace file modifications
- `chat_message` — New messages from agents
- `agent_streaming` — Live agent output (typing indicator)

### UI Proxy (Access from Any Node)

Each slave node runs a lightweight reverse proxy:

```python
class UIProxy:
    """Proxy UI requests to master node."""

    def __init__(self, master_url: str, local_port: int = 8080):
        self.master_url = master_url
        self.port = local_port

    async def proxy_request(self, request):
        """Forward request to master's UI backend."""
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=f"{self.master_url}{request.url.path}",
                headers=request.headers,
                content=await request.body()
            )
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
```

This means `http://device-a:8080`, `http://device-b:8080`, etc. all show the same UI.

### Frontend Tech Stack

```
ui/
├── package.json          # React 18, Vite 5, Tailwind CSS 3
├── vite.config.ts
├── src/
│   ├── App.tsx           # Router, layout, WebSocket provider
│   ├── api/
│   │   ├── client.ts     # HTTP client (fetch wrapper)
│   │   └── ws.ts         # WebSocket connection manager
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── Chat.tsx
│   │   ├── Approvals.tsx
│   │   ├── FileExplorer.tsx
│   │   └── Settings.tsx
│   ├── components/
│   │   ├── AgentCard.tsx
│   │   ├── ChatMessage.tsx
│   │   ├── IntentReview.tsx
│   │   ├── FileTree.tsx
│   │   ├── ActivityFeed.tsx
│   │   └── StatusBadge.tsx
│   └── hooks/
│       ├── useWebSocket.ts
│       ├── useAgents.ts
│       └── useApprovals.ts
└── index.html
```

## Testing Plan

1. **API tests**: All REST endpoints return correct data
2. **WebSocket**: Events pushed in real-time
3. **UI proxy**: Requests forwarded correctly from slave nodes
4. **Chat flow**: Message → agent response → streaming display
5. **Approval flow**: Intent appears → approve/reject → agent proceeds
6. **Responsive**: UI works on desktop and tablet
7. **Multi-user**: Two browsers open simultaneously see same state

## Success Criteria

- [ ] `http://<any-node>:8080` loads the dashboard
- [ ] Dashboard shows all agents with live status
- [ ] Chat sends messages and displays streaming responses
- [ ] Intent approvals work with approve/reject buttons
- [ ] File explorer shows shared workspace with syntax highlighting
- [ ] WebSocket delivers real-time updates (< 500ms latency)
- [ ] Settings page allows changing autonomy level and agent roles
