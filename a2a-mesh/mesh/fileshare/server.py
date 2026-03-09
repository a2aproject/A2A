"""HTTP-based file server for the mesh workspace."""

from __future__ import annotations

import logging
import mimetypes
from pathlib import Path
from datetime import datetime, timezone

from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse
from starlette.routing import Route, Router

logger = logging.getLogger(__name__)


class FileShareServer:
    """HTTP file server for shared workspace access across the mesh.

    All agents can read/write files through this server.
    Hosted on the master node.
    """

    def __init__(self, root_dir: str):
        self.root = Path(root_dir)
        self.root.mkdir(parents=True, exist_ok=True)
        self._modifications: list[dict] = []

    def _resolve(self, path: str) -> Path:
        """Resolve path safely, preventing directory traversal."""
        # Normalize and resolve
        clean_path = path.lstrip("/")
        resolved = (self.root / clean_path).resolve()

        # Ensure it's within root
        if not str(resolved).startswith(str(self.root.resolve())):
            raise ValueError("Path traversal detected")

        return resolved

    def _file_info(self, path: Path, relative_to: Path | None = None) -> dict:
        """Get file metadata."""
        rel = path.relative_to(relative_to or self.root)
        stat = path.stat()
        return {
            "path": str(rel),
            "name": path.name,
            "is_dir": path.is_dir(),
            "size": stat.st_size if path.is_file() else 0,
            "modified": datetime.fromtimestamp(
                stat.st_mtime, tz=timezone.utc
            ).isoformat(),
            "content_type": mimetypes.guess_type(path.name)[0] or "application/octet-stream",
        }


# ---- Singleton instance ----
_server: FileShareServer | None = None


def get_server() -> FileShareServer:
    global _server
    if _server is None:
        _server = FileShareServer("/tmp/mesh-workspace")
    return _server


def init_server(root_dir: str) -> FileShareServer:
    global _server
    _server = FileShareServer(root_dir)
    return _server


# ---- Route handlers ----


async def handle_get_file(request: Request) -> Response:
    """GET /files/{path} — Download file or get metadata."""
    server = get_server()
    path = request.path_params.get("path", "")

    try:
        resolved = server._resolve(path)
    except ValueError:
        return JSONResponse({"error": "Invalid path"}, status_code=400)

    if not resolved.exists():
        return JSONResponse({"error": "Not found"}, status_code=404)

    # Metadata request
    if "meta" in request.query_params:
        return JSONResponse(server._file_info(resolved))

    # Directory listing
    if resolved.is_dir():
        items = []
        for child in sorted(resolved.iterdir()):
            items.append(server._file_info(child))
        return JSONResponse(items)

    # File download
    content_type = mimetypes.guess_type(resolved.name)[0] or "application/octet-stream"
    return Response(
        content=resolved.read_bytes(),
        media_type=content_type,
        headers={"X-File-Size": str(resolved.stat().st_size)},
    )


async def handle_put_file(request: Request) -> JSONResponse:
    """PUT /files/{path} — Upload/overwrite file."""
    server = get_server()
    path = request.path_params.get("path", "")
    agent_id = request.headers.get("X-Agent-ID", "unknown")

    try:
        resolved = server._resolve(path)
    except ValueError:
        return JSONResponse({"error": "Invalid path"}, status_code=400)

    # Create parent directories
    resolved.parent.mkdir(parents=True, exist_ok=True)

    # Write content
    body = await request.body()
    resolved.write_bytes(body)

    server._modifications.append({
        "path": path,
        "agent_id": agent_id,
        "action": "write",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "size": len(body),
    })

    logger.info(f"File written: {path} by {agent_id} ({len(body)} bytes)")
    return JSONResponse({"status": "written", "path": path, "size": len(body)})


async def handle_delete_file(request: Request) -> JSONResponse:
    """DELETE /files/{path} — Delete file."""
    server = get_server()
    path = request.path_params.get("path", "")
    agent_id = request.headers.get("X-Agent-ID", "unknown")

    try:
        resolved = server._resolve(path)
    except ValueError:
        return JSONResponse({"error": "Invalid path"}, status_code=400)

    if not resolved.exists():
        return JSONResponse({"error": "Not found"}, status_code=404)

    if resolved.is_dir():
        import shutil
        shutil.rmtree(resolved)
    else:
        resolved.unlink()

    logger.info(f"File deleted: {path} by {agent_id}")
    return JSONResponse({"status": "deleted", "path": path})


async def handle_list_files(request: Request) -> JSONResponse:
    """GET /files/ — List root directory or search."""
    server = get_server()

    # Search
    query = request.query_params.get("search")
    if query:
        results = []
        for p in server.root.rglob("*"):
            if p.is_file():
                try:
                    content = p.read_text(errors="ignore")
                    for i, line in enumerate(content.split("\n"), 1):
                        if query.lower() in line.lower():
                            results.append({
                                "path": str(p.relative_to(server.root)),
                                "line": i,
                                "text": line.strip()[:200],
                            })
                            if len(results) >= 100:
                                break
                except Exception:
                    pass
            if len(results) >= 100:
                break
        return JSONResponse(results)

    # Tree
    if "tree" in request.query_params:
        tree = _build_tree(server.root, server.root)
        return JSONResponse(tree)

    # Directory listing
    dir_path = request.query_params.get("dir", "")
    try:
        resolved = server._resolve(dir_path)
    except ValueError:
        return JSONResponse({"error": "Invalid path"}, status_code=400)

    if not resolved.exists() or not resolved.is_dir():
        return JSONResponse({"error": "Not a directory"}, status_code=400)

    items = []
    for child in sorted(resolved.iterdir()):
        items.append(server._file_info(child))
    return JSONResponse(items)


async def handle_mkdir(request: Request) -> JSONResponse:
    """POST /files/?mkdir={path} — Create directory."""
    server = get_server()
    path = request.query_params.get("mkdir", "")

    if not path:
        return JSONResponse({"error": "mkdir param required"}, status_code=400)

    try:
        resolved = server._resolve(path)
    except ValueError:
        return JSONResponse({"error": "Invalid path"}, status_code=400)

    resolved.mkdir(parents=True, exist_ok=True)
    return JSONResponse({"status": "created", "path": path})


def _build_tree(path: Path, root: Path, depth: int = 0, max_depth: int = 5) -> dict:
    """Build a directory tree structure."""
    info = {
        "name": path.name or str(root),
        "path": str(path.relative_to(root)) if path != root else "",
        "is_dir": path.is_dir(),
    }
    if path.is_dir() and depth < max_depth:
        info["children"] = [
            _build_tree(child, root, depth + 1, max_depth)
            for child in sorted(path.iterdir())
            if not child.name.startswith(".")
        ]
    return info


def create_fileshare_routes() -> Router:
    """Create Starlette routes for the file share API."""
    return Router(
        routes=[
            Route("/files/", handle_list_files, methods=["GET"]),
            Route("/files/", handle_mkdir, methods=["POST"]),
            Route("/files/{path:path}", handle_get_file, methods=["GET"]),
            Route("/files/{path:path}", handle_put_file, methods=["PUT"]),
            Route("/files/{path:path}", handle_delete_file, methods=["DELETE"]),
        ]
    )
