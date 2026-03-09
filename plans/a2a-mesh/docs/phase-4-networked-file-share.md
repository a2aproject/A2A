# Phase 4: Networked File Share

## Goal

All agents in the mesh share a common workspace so they can read, write, and collaborate on files. An agent on Device A creates a file, an agent on Device B can immediately read it.

## Deliverables

1. `mesh/fileshare/server.py` — HTTP-based file server hosted on master
2. `mesh/fileshare/client.py` — File operations client for agents
3. `mesh/fileshare/sync.py` — Optional local caching/sync for performance
4. Agent tools: `read_file`, `write_file`, `list_files` wired to file share

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                 MASTER NODE                           │
│  ┌────────────────────────────────────────────────┐  │
│  │           File Share Server (:9001)             │  │
│  │  /workspace/                                    │  │
│  │  ├── src/                                       │  │
│  │  ├── docs/                                      │  │
│  │  ├── tests/                                     │  │
│  │  └── .agents/  (agent metadata, logs)           │  │
│  └────────────────────────────────────────────────┘  │
└──────┬───────────────────────┬───────────────────────┘
       │ HTTP                  │ HTTP
┌──────▼──────┐         ┌─────▼───────┐
│ Slave A     │         │ Slave B     │
│ read_file() │         │ write_file()│
│ write_file()│         │ read_file() │
│             │         │             │
│ Local cache │         │ Local cache │
│ /tmp/mesh/  │         │ /tmp/mesh/  │
└─────────────┘         └─────────────┘
```

## Why HTTP File Server (Not NFS/SMB/FUSE)

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| NFS | Fast, native | Complex setup, Linux-centric, permission issues | Too complex |
| SMB/CIFS | Cross-platform | Windows-centric, auth complexity | Over-engineered |
| FUSE mount | Transparent | Kernel module needed, fragile | Too fragile |
| **HTTP REST** | Simple, cross-platform, works everywhere | Slightly slower | **Best for MVP** |
| WebDAV | Standard protocol | Complex spec | Future option |

## API Design

### File Server REST API (`/files/`)

```
GET    /files/{path}           Download file content
PUT    /files/{path}           Upload/overwrite file
POST   /files/{path}           Create new file (fails if exists)
DELETE /files/{path}           Delete file
PATCH  /files/{path}           Append to file

GET    /files/{path}?meta      Get file metadata (size, modified, etc.)
GET    /files/?list&dir={path} List directory contents
POST   /files/?mkdir={path}    Create directory
POST   /files/?move            Move/rename file
POST   /files/?copy            Copy file

GET    /files/?search={query}  Search file contents (grep)
GET    /files/?tree             Full directory tree
GET    /files/?watch={path}     SSE stream of file changes
```

### File Metadata Response
```json
{
  "path": "src/parser.py",
  "size": 2048,
  "modified": "2025-01-15T10:30:00Z",
  "modified_by": "coder-agent",
  "content_type": "text/x-python",
  "checksum": "sha256:abc123..."
}
```

## Implementation

### File Server (`mesh/fileshare/server.py`)

```python
class FileShareServer:
    """HTTP-based file server for the mesh workspace."""

    def __init__(self, root_dir: str, port: int = 9001):
        self.root = Path(root_dir)
        self.port = port
        self.watchers: dict[str, list[EventQueue]] = {}

    async def get_file(self, path: str) -> FileResponse:
        """Read and return file contents."""
        full_path = self._resolve(path)
        if not full_path.exists():
            raise FileNotFound(path)
        return FileResponse(full_path)

    async def put_file(self, path: str, content: bytes, agent_id: str):
        """Write file contents. Creates parent dirs if needed."""
        full_path = self._resolve(path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(content)
        # Track who modified it
        await self._record_modification(path, agent_id)
        # Notify watchers
        await self._notify_watchers(path, "modified")

    async def list_dir(self, path: str) -> list[FileInfo]:
        """List directory contents with metadata."""

    async def search(self, query: str, path: str = "") -> list[SearchResult]:
        """Search file contents (grep-like)."""

    async def watch(self, path: str) -> AsyncGenerator[FileEvent, None]:
        """SSE stream of file changes in path."""

    def _resolve(self, path: str) -> Path:
        """Resolve path safely (prevent directory traversal)."""
        resolved = (self.root / path).resolve()
        if not resolved.is_relative_to(self.root):
            raise SecurityError("Path traversal detected")
        return resolved
```

### File Client (`mesh/fileshare/client.py`)

```python
class FileShareClient:
    """Client for accessing the mesh file share."""

    def __init__(self, server_url: str, agent_id: str):
        self.server_url = server_url
        self.agent_id = agent_id
        self.cache = LocalCache("/tmp/mesh-cache")

    async def read(self, path: str) -> str:
        """Read file contents as string."""
        # Check cache first
        cached = self.cache.get(path)
        if cached and not cached.expired:
            return cached.content
        # Fetch from server
        response = await httpx.get(f"{self.server_url}/files/{path}")
        content = response.text
        self.cache.put(path, content)
        return content

    async def write(self, path: str, content: str):
        """Write content to file."""
        await httpx.put(
            f"{self.server_url}/files/{path}",
            content=content,
            headers={"X-Agent-ID": self.agent_id}
        )
        self.cache.invalidate(path)

    async def list(self, path: str = "") -> list[FileInfo]:
        """List directory contents."""

    async def search(self, query: str) -> list[SearchResult]:
        """Search file contents."""

    async def watch(self, path: str, callback):
        """Watch for file changes (SSE)."""
```

### Agent Tools (wired into Phase 1 tool system)

```python
# Registered as tools available to all agents

async def tool_read_file(path: str) -> str:
    """Read a file from the shared workspace."""
    return await fileshare_client.read(path)

async def tool_write_file(path: str, content: str) -> str:
    """Write content to a file in the shared workspace."""
    await fileshare_client.write(path, content)
    return f"Written {len(content)} bytes to {path}"

async def tool_list_files(path: str = "") -> str:
    """List files in the shared workspace."""
    files = await fileshare_client.list(path)
    return "\n".join(f.path for f in files)

async def tool_search_files(query: str) -> str:
    """Search for text in files."""
    results = await fileshare_client.search(query)
    return "\n".join(f"{r.path}:{r.line}: {r.text}" for r in results)
```

## File Locking (Conflict Prevention)

Simple advisory locking to prevent two agents editing the same file:

```python
class FileLockManager:
    """Advisory file locks for concurrent agent access."""

    async def acquire(self, path: str, agent_id: str, timeout: int = 30) -> Lock:
        """Acquire advisory lock on a file."""

    async def release(self, path: str, agent_id: str):
        """Release lock."""

    async def is_locked(self, path: str) -> Optional[LockInfo]:
        """Check if file is locked and by whom."""
```

Locks are advisory — agents should check, but the system doesn't hard-block writes.

## Performance

- **Local cache**: Frequently read files cached on each node with TTL
- **Cache invalidation**: Via file watch SSE — instant invalidation on change
- **Large files**: Streamed, not buffered in memory
- **Binary files**: Supported (images, archives, etc.)

## Testing Plan

1. **CRUD**: Create, read, update, delete files via API
2. **Directory operations**: mkdir, list, tree
3. **Concurrent access**: Two agents writing different files simultaneously
4. **File locking**: Lock acquire, release, timeout
5. **Path traversal**: Verify `../../etc/passwd` is blocked
6. **Large files**: 100MB+ file upload/download
7. **File watch**: SSE notifications on file changes
8. **Search**: Grep-like search across workspace

## Success Criteria

- [ ] Agents can read/write files across the network via tools
- [ ] File changes on one node are immediately visible to others
- [ ] Directory traversal attacks are prevented
- [ ] File locking prevents concurrent write conflicts
- [ ] File change notifications work via SSE
- [ ] Local caching reduces network calls for frequently read files
