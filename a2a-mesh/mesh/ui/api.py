"""REST API backend for the Web UI."""

from __future__ import annotations

import logging

from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route, Router

from mesh.network.registry import get_registry
from mesh.orchestrator.intent import IntentQueue

logger = logging.getLogger(__name__)

# Module-level references set during server setup
_intent_queue: IntentQueue | None = None
_orchestrator = None


def set_orchestrator(orchestrator):
    global _orchestrator, _intent_queue
    _orchestrator = orchestrator
    if orchestrator:
        _intent_queue = orchestrator.intent_queue


# ---- Dashboard ----


async def handle_dashboard(request: Request) -> HTMLResponse:
    """GET / — Serve the dashboard HTML (single-page app shell)."""
    return HTMLResponse(DASHBOARD_HTML)


async def handle_cluster_status(request: Request) -> JSONResponse:
    """GET /api/cluster/status — Cluster overview."""
    registry = get_registry()
    agents = registry.get_all_agents()
    healthy = [a for a in agents if a.healthy]
    return JSONResponse({
        "total_agents": len(agents),
        "healthy_agents": len(healthy),
        "agents": [a.to_dict() for a in agents],
    })


async def handle_agents(request: Request) -> JSONResponse:
    """GET /api/agents — List all agents."""
    registry = get_registry()
    return JSONResponse([a.to_dict() for a in registry.get_all_agents()])


async def handle_agent_detail(request: Request) -> JSONResponse:
    """GET /api/agents/{agent_id} — Agent detail."""
    agent_id = request.path_params["agent_id"]
    agent = get_registry().get_agent(agent_id)
    if not agent:
        return JSONResponse({"error": "Not found"}, status_code=404)
    return JSONResponse(agent.to_dict())


# ---- Chat ----


async def handle_chat_send(request: Request) -> JSONResponse:
    """POST /api/chat/send — Send message to orchestrator."""
    body = await request.json()
    message = body.get("message", "")

    if not message:
        return JSONResponse({"error": "message required"}, status_code=400)

    if not _orchestrator:
        return JSONResponse({"error": "Orchestrator not initialized"}, status_code=503)

    try:
        plan = await _orchestrator.handle_user_request(message)
        result = await _orchestrator.execute_plan(plan)
        return JSONResponse({
            "plan_id": result.plan_id,
            "status": result.status,
            "steps": [
                {
                    "step": s.step,
                    "description": s.description,
                    "agent": s.agent.name if s.agent else None,
                    "status": s.status,
                    "result": s.result,
                }
                for s in result.steps
            ],
        })
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        return JSONResponse({"error": str(e)}, status_code=500)


# ---- Approvals ----


async def handle_pending_approvals(request: Request) -> JSONResponse:
    """GET /api/approvals/pending — List pending intents."""
    if not _intent_queue:
        return JSONResponse([])
    pending = _intent_queue.get_pending()
    return JSONResponse([i.to_dict() for i in pending])


async def handle_approve_intent(request: Request) -> JSONResponse:
    """POST /api/approvals/{intent_id}/approve — Approve an intent."""
    intent_id = request.path_params["intent_id"]
    if not _intent_queue:
        return JSONResponse({"error": "No intent queue"}, status_code=503)
    if _intent_queue.approve(intent_id, by="human"):
        return JSONResponse({"status": "approved"})
    return JSONResponse({"error": "Intent not found"}, status_code=404)


async def handle_reject_intent(request: Request) -> JSONResponse:
    """POST /api/approvals/{intent_id}/reject — Reject an intent."""
    intent_id = request.path_params["intent_id"]
    body = await request.json()
    reason = body.get("reason", "")
    if not _intent_queue:
        return JSONResponse({"error": "No intent queue"}, status_code=503)
    if _intent_queue.reject(intent_id, by="human", reason=reason):
        return JSONResponse({"status": "rejected"})
    return JSONResponse({"error": "Intent not found"}, status_code=404)


async def handle_approval_history(request: Request) -> JSONResponse:
    """GET /api/approvals/history — Approval history."""
    if not _intent_queue:
        return JSONResponse([])
    return JSONResponse(_intent_queue.get_history())


# ---- Settings ----


async def handle_get_settings(request: Request) -> JSONResponse:
    """GET /api/settings — Get current settings."""
    return JSONResponse({
        "autonomy_level": 1,
        "auto_approve_skills": ["research", "summarize"],
        "require_approval_skills": ["execute_command", "deploy"],
    })


def create_ui_routes() -> Router:
    """Create Starlette routes for the UI API."""
    return Router(
        routes=[
            # Dashboard
            Route("/", handle_dashboard, methods=["GET"]),
            Route("/api/cluster/status", handle_cluster_status, methods=["GET"]),
            Route("/api/agents", handle_agents, methods=["GET"]),
            Route("/api/agents/{agent_id}", handle_agent_detail, methods=["GET"]),
            # Chat
            Route("/api/chat/send", handle_chat_send, methods=["POST"]),
            # Approvals
            Route("/api/approvals/pending", handle_pending_approvals, methods=["GET"]),
            Route(
                "/api/approvals/{intent_id}/approve",
                handle_approve_intent,
                methods=["POST"],
            ),
            Route(
                "/api/approvals/{intent_id}/reject",
                handle_reject_intent,
                methods=["POST"],
            ),
            Route("/api/approvals/history", handle_approval_history, methods=["GET"]),
            # Settings
            Route("/api/settings", handle_get_settings, methods=["GET"]),
        ]
    )


# ---- Embedded Dashboard HTML ----
# Minimal SPA that calls the API. Replace with full React build in production.

DASHBOARD_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>A2A Mesh Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #e2e8f0; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        header { display: flex; justify-content: space-between; align-items: center; padding: 16px 0; border-bottom: 1px solid #334155; margin-bottom: 24px; }
        header h1 { font-size: 1.5rem; color: #38bdf8; }
        .status-badge { padding: 4px 12px; border-radius: 9999px; font-size: 0.875rem; }
        .status-online { background: #064e3b; color: #6ee7b7; }
        .status-offline { background: #7f1d1d; color: #fca5a5; }
        .tabs { display: flex; gap: 8px; margin-bottom: 24px; }
        .tab { padding: 8px 16px; border-radius: 8px; cursor: pointer; background: #1e293b; border: 1px solid #334155; color: #94a3b8; }
        .tab.active { background: #38bdf8; color: #0f172a; border-color: #38bdf8; }
        .agent-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
        .agent-card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 16px; }
        .agent-card h3 { color: #38bdf8; margin-bottom: 8px; }
        .agent-card .meta { font-size: 0.875rem; color: #94a3b8; }
        .agent-card .skills { margin-top: 8px; display: flex; flex-wrap: wrap; gap: 4px; }
        .skill-tag { padding: 2px 8px; border-radius: 4px; background: #334155; font-size: 0.75rem; color: #cbd5e1; }
        .chat-container { display: flex; flex-direction: column; height: calc(100vh - 200px); }
        .chat-messages { flex: 1; overflow-y: auto; padding: 16px 0; }
        .chat-message { margin-bottom: 12px; padding: 12px; border-radius: 8px; }
        .chat-message.user { background: #1e3a5f; margin-left: 20%; }
        .chat-message.agent { background: #1e293b; margin-right: 20%; }
        .chat-input { display: flex; gap: 8px; padding: 16px 0; }
        .chat-input input { flex: 1; padding: 12px; border-radius: 8px; border: 1px solid #334155; background: #1e293b; color: #e2e8f0; font-size: 1rem; }
        .chat-input button { padding: 12px 24px; border-radius: 8px; background: #38bdf8; color: #0f172a; border: none; font-weight: 600; cursor: pointer; }
        .chat-input button:hover { background: #7dd3fc; }
        .approval-card { background: #1e293b; border: 1px solid #f59e0b; border-radius: 12px; padding: 16px; margin-bottom: 12px; }
        .approval-actions { display: flex; gap: 8px; margin-top: 12px; }
        .btn-approve { padding: 8px 16px; border-radius: 8px; background: #059669; color: white; border: none; cursor: pointer; }
        .btn-reject { padding: 8px 16px; border-radius: 8px; background: #dc2626; color: white; border: none; cursor: pointer; }
        .loading { text-align: center; padding: 40px; color: #64748b; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>A2A Mesh Dashboard</h1>
            <div id="cluster-status" class="status-badge status-online">Loading...</div>
        </header>

        <div class="tabs">
            <div class="tab active" onclick="showTab('dashboard')">Dashboard</div>
            <div class="tab" onclick="showTab('chat')">Chat</div>
            <div class="tab" onclick="showTab('approvals')">Approvals</div>
        </div>

        <div id="dashboard-tab">
            <div id="agent-grid" class="agent-grid">
                <div class="loading">Loading agents...</div>
            </div>
        </div>

        <div id="chat-tab" style="display:none">
            <div class="chat-container">
                <div id="chat-messages" class="chat-messages"></div>
                <div class="chat-input">
                    <input type="text" id="chat-input" placeholder="Send a task to the mesh..." onkeypress="if(event.key==='Enter')sendChat()">
                    <button onclick="sendChat()">Send</button>
                </div>
            </div>
        </div>

        <div id="approvals-tab" style="display:none">
            <div id="approvals-list">
                <div class="loading">Loading approvals...</div>
            </div>
        </div>
    </div>

    <script>
        let currentTab = 'dashboard';

        function showTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('[id$="-tab"]').forEach(t => t.style.display = 'none');
            event.target.classList.add('active');
            document.getElementById(tab + '-tab').style.display = 'block';
            currentTab = tab;
            if (tab === 'dashboard') loadAgents();
            if (tab === 'approvals') loadApprovals();
        }

        async function loadAgents() {
            try {
                const resp = await fetch('/api/agents');
                const agents = await resp.json();
                const grid = document.getElementById('agent-grid');
                if (agents.length === 0) {
                    grid.innerHTML = '<div class="loading">No agents registered yet.</div>';
                    return;
                }
                grid.innerHTML = agents.map(a => `
                    <div class="agent-card">
                        <h3>${a.role === 'master' ? '★ ' : ''}${a.name}</h3>
                        <div class="meta">
                            <span class="status-badge ${a.healthy ? 'status-online' : 'status-offline'}">
                                ${a.healthy ? '● Online' : '● Offline'}
                            </span>
                        </div>
                        <div class="meta" style="margin-top:8px">
                            LLM: ${a.llm_model || 'N/A'}<br>
                            ${a.url || a.host + ':' + a.port}
                        </div>
                        <div class="skills">
                            ${(a.skill_tags || []).map(s => `<span class="skill-tag">${s}</span>`).join('')}
                        </div>
                    </div>
                `).join('');
            } catch (e) {
                document.getElementById('agent-grid').innerHTML = '<div class="loading">Error loading agents</div>';
            }
        }

        async function loadClusterStatus() {
            try {
                const resp = await fetch('/api/cluster/status');
                const data = await resp.json();
                document.getElementById('cluster-status').textContent =
                    `● ${data.healthy_agents}/${data.total_agents} agents online`;
                document.getElementById('cluster-status').className =
                    'status-badge ' + (data.healthy_agents > 0 ? 'status-online' : 'status-offline');
            } catch (e) {
                document.getElementById('cluster-status').textContent = '● Disconnected';
                document.getElementById('cluster-status').className = 'status-badge status-offline';
            }
        }

        async function sendChat() {
            const input = document.getElementById('chat-input');
            const message = input.value.trim();
            if (!message) return;

            const messages = document.getElementById('chat-messages');
            messages.innerHTML += `<div class="chat-message user">${message}</div>`;
            input.value = '';

            try {
                messages.innerHTML += `<div class="chat-message agent" id="thinking">Thinking...</div>`;
                const resp = await fetch('/api/chat/send', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message})
                });
                const data = await resp.json();
                document.getElementById('thinking').remove();

                if (data.error) {
                    messages.innerHTML += `<div class="chat-message agent">Error: ${data.error}</div>`;
                } else {
                    let html = `<div class="chat-message agent"><strong>Plan (${data.status}):</strong><br>`;
                    for (const step of data.steps || []) {
                        const icon = step.status === 'completed' ? '✅' : step.status === 'failed' ? '❌' : '⏳';
                        html += `${icon} Step ${step.step}: ${step.description}`;
                        if (step.agent) html += ` → ${step.agent}`;
                        html += '<br>';
                    }
                    html += '</div>';
                    messages.innerHTML += html;
                }
            } catch (e) {
                document.getElementById('thinking')?.remove();
                messages.innerHTML += `<div class="chat-message agent">Error: ${e.message}</div>`;
            }
            messages.scrollTop = messages.scrollHeight;
        }

        async function loadApprovals() {
            try {
                const resp = await fetch('/api/approvals/pending');
                const pending = await resp.json();
                const list = document.getElementById('approvals-list');
                if (pending.length === 0) {
                    list.innerHTML = '<div class="loading">No pending approvals.</div>';
                    return;
                }
                list.innerHTML = pending.map(i => `
                    <div class="approval-card">
                        <strong>${i.agent_name}</strong> → ${i.action}<br>
                        <div class="meta" style="margin-top:4px">${i.description}</div>
                        <div class="meta">Risk: ${i.risk_level}</div>
                        <div class="approval-actions">
                            <button class="btn-approve" onclick="approveIntent('${i.intent_id}')">✅ Approve</button>
                            <button class="btn-reject" onclick="rejectIntent('${i.intent_id}')">❌ Reject</button>
                        </div>
                    </div>
                `).join('');
            } catch (e) {
                document.getElementById('approvals-list').innerHTML = '<div class="loading">Error loading approvals</div>';
            }
        }

        async function approveIntent(id) {
            await fetch(`/api/approvals/${id}/approve`, {method: 'POST'});
            loadApprovals();
        }

        async function rejectIntent(id) {
            await fetch(`/api/approvals/${id}/reject`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({reason: 'Rejected by user'})
            });
            loadApprovals();
        }

        // Initial load
        loadAgents();
        loadClusterStatus();
        // Auto-refresh
        setInterval(() => {
            loadClusterStatus();
            if (currentTab === 'dashboard') loadAgents();
            if (currentTab === 'approvals') loadApprovals();
        }, 5000);
    </script>
</body>
</html>
"""
