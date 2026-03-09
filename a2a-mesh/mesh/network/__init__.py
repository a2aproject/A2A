"""Network layer — mDNS discovery, registry, star topology."""

from mesh.network.discovery import MeshDiscovery
from mesh.network.registry import AgentRegistry
from mesh.network.topology import StarTopology

__all__ = ["MeshDiscovery", "AgentRegistry", "StarTopology"]
