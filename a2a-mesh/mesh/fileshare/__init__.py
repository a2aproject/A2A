"""Networked file share — HTTP-based shared workspace."""

from mesh.fileshare.server import FileShareServer
from mesh.fileshare.client import FileShareClient

__all__ = ["FileShareServer", "FileShareClient"]
