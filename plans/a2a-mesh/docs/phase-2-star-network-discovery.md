# Phase 2: Star Network & Auto-Discovery

## Goal

Enable agents across multiple devices on a LAN to automatically discover each other and form a star network topology with a single master node at the center.

## Deliverables

1. `mesh/network/discovery.py` — mDNS/DNS-SD service announcement and discovery
2. `mesh/network/registry.py` — Master-hosted agent registry with REST API
3. `mesh/network/topology.py` — Star topology manager (join, leave, heartbeat)
4. `mesh/network/models.py` — Network data models

## How It Works

### Startup Flow

```
┌──────────────┐     1. Announce via mDNS      ┌──────────────────┐
│  Master Node │ ◄─────────────────────────────│  Network (LAN)   │
│  port 9000   │ ────────────────────────────► │                  │
└──────┬───────┘     "_a2a-mesh._tcp.local."   └──────────────────┘
       │                                              ▲  ▲
       │                                              │  │
       │                                              │  │
┌──────▼───────┐     2. Discover master via mDNS      │  │
│  Slave Node  │ ─────────────────────────────────────┘  │
│  port 10001  │     3. Register with master              │
│              │ ─────────────────────────────────────────┘
│              │     4. Start heartbeat
└──────────────┘
```

### Detailed Sequence

1. **Master starts** → announces `_a2a-mesh-master._tcp.local.` via mDNS
2. **Master starts registry** → HTTP API at `http://{master}:9000/registry/`
3. **Slave starts** → browses mDNS for `_a2a-mesh-master._tcp.local.`
4. **Slave finds master** → resolves master IP:port from mDNS record
5. **Slave registers** → `POST /registry/agents` with its Agent Card
6. **Master acknowledges** → returns cluster config (file share URL, other agents)
7. **Heartbeat loop** → Slave pings master every 15s, master marks dead agents after 45s
8. **Slave shuts down** → `DELETE /registry/agents/{id}` deregisters cleanly

### Fallback: Direct Configuration

If mDNS is blocked or unreliable:

```yaml
# In slave config
master:
  discover: false
  url: "http://192.168.1.100:9000"
```

## Implementation Detail

### mDNS Discovery (`mesh/network/discovery.py`)

Uses Python `zeroconf` library for zero-config networking:

```python
class MeshDiscovery:
    """mDNS service announcement and discovery for A2A mesh."""

    SERVICE_TYPE = "_a2a-mesh._tcp.local."
    MASTER_SERVICE_TYPE = "_a2a-mesh-master._tcp.local."

    async def announce_master(self, name, host, port, metadata):
        """Announce this node as the mesh master."""
        # Register mDNS service with TXT records containing:
        # - node_id: unique identifier
        # - api_version: mesh protocol version
        # - registry_port: port for agent registry
        # - fileshare_port: port for file share

    async def announce_slave(self, name, host, port, metadata):
        """Announce this node as a mesh slave."""

    async def discover_master(self, timeout=10) -> MasterInfo:
        """Browse for master node on LAN. Returns first found."""

    async def discover_all_nodes(self, timeout=5) -> list[NodeInfo]:
        """Browse for all mesh nodes on LAN."""

    async def stop(self):
        """Unregister mDNS services."""
```

### Agent Registry (`mesh/network/registry.py`)

REST API hosted on the master node:

```
POST   /registry/agents              Register agent (sends AgentCard + node info)
GET    /registry/agents              List all registered agents
GET    /registry/agents/{agent_id}   Get specific agent
DELETE /registry/agents/{agent_id}   Deregister agent
POST   /registry/agents/{id}/heartbeat   Agent heartbeat
GET    /registry/agents?skill={tag}  Find agents by skill tag
GET    /registry/agents?role={role}  Find agents by role
GET    /registry/status              Cluster status summary
```

**Agent Registration Payload:**
```json
{
  "node_id": "node-abc123",
  "agent_card": { /* standard A2A AgentCard */ },
  "node_info": {
    "hostname": "device-b.local",
    "ip": "192.168.1.101",
    "port": 10001,
    "role": "slave",
    "llm_model": "qwen2.5:14b",
    "llm_provider": "ollama"
  }
}
```

**Registry Response:**
```json
{
  "agent_id": "agent-xyz789",
  "registered_at": "2025-01-15T10:30:00Z",
  "cluster_config": {
    "master_url": "http://192.168.1.100:9000",
    "fileshare_url": "http://192.168.1.100:9001",
    "peers": [
      {"name": "researcher", "url": "http://192.168.1.102:10002"}
    ]
  }
}
```

### Star Topology Manager (`mesh/network/topology.py`)

```python
class StarTopology:
    """Manages star network with master at center."""

    def __init__(self, role: str, registry_url: str = None):
        self.role = role  # "master" or "slave"
        self.nodes: dict[str, NodeInfo] = {}
        self.heartbeat_interval = 15  # seconds
        self.dead_threshold = 45      # seconds

    # Master methods
    async def accept_registration(self, agent_card, node_info) -> str:
        """Register a new slave node. Returns agent_id."""

    async def check_heartbeats(self):
        """Background task: mark unresponsive nodes as dead."""

    async def broadcast_topology_change(self, event):
        """Notify all slaves when topology changes (node join/leave)."""

    async def get_agent_for_skill(self, skill_tag: str) -> NodeInfo:
        """Find best agent for a given skill."""

    # Slave methods
    async def register_with_master(self, master_url, agent_card):
        """Register this slave with the master."""

    async def start_heartbeat(self):
        """Background task: ping master every 15s."""

    async def handle_topology_update(self, event):
        """React to topology changes from master."""
```

### Health Monitoring

```python
class HealthMonitor:
    """Monitors agent health and LLM backend availability."""

    async def check_agent_health(self, agent_url) -> HealthStatus:
        """Ping agent's A2A endpoint."""

    async def check_llm_health(self, llm_config) -> HealthStatus:
        """Verify LLM backend is responding."""

    async def get_cluster_health(self) -> ClusterHealth:
        """Aggregate health across all nodes."""
```

**Health status includes:**
- Agent HTTP reachability
- LLM backend status
- Memory/CPU usage (optional)
- Current task load
- Last heartbeat timestamp

## Network Security Considerations

For local/home networks (MVP):
- No authentication required (trusted LAN)
- HTTP only (no TLS)
- Firewall rules optional

For production/office networks (future):
- mTLS between nodes
- API key for registry access
- Agent Card authentication
- Network segmentation support

## Testing Plan

1. **mDNS announce/discover**: Master announces, slave discovers on same machine (loopback)
2. **Registry CRUD**: Register, list, get, delete agents
3. **Heartbeat timeout**: Verify dead agent detection after 45s
4. **Multi-node simulation**: 3 agents on different ports, verify full topology
5. **Failover**: Master restart → slaves re-register automatically
6. **Direct config fallback**: Verify slaves can connect without mDNS

## Success Criteria

- [ ] Master announces via mDNS and is discoverable within 5 seconds
- [ ] Slave auto-discovers master and registers without manual config
- [ ] Dead agents are detected and removed within 60 seconds
- [ ] Topology changes are broadcast to all nodes
- [ ] `mesh agents list` shows all agents across all devices
- [ ] Fallback to direct URL config works when mDNS is unavailable
