"""mDNS/DNS-SD service announcement and discovery."""

from __future__ import annotations

import asyncio
import logging
import socket
from typing import Callable

from zeroconf import IPVersion, ServiceInfo, ServiceStateChange, Zeroconf
from zeroconf.asyncio import AsyncServiceBrowser, AsyncServiceInfo, AsyncZeroconf

from mesh.network.models import MasterInfo, NodeInfo

logger = logging.getLogger(__name__)

MASTER_SERVICE_TYPE = "_a2a-mesh-master._tcp.local."
AGENT_SERVICE_TYPE = "_a2a-mesh._tcp.local."


class MeshDiscovery:
    """mDNS-based service discovery for the A2A mesh network.

    Master nodes announce themselves so slave nodes can auto-discover
    them without any manual configuration.
    """

    def __init__(self):
        self._zeroconf: AsyncZeroconf | None = None
        self._browser: AsyncServiceBrowser | None = None
        self._service_info: ServiceInfo | None = None

    async def _ensure_zeroconf(self):
        if self._zeroconf is None:
            self._zeroconf = AsyncZeroconf(ip_version=IPVersion.V4Only)

    async def announce_master(
        self,
        name: str,
        host: str,
        port: int,
        node_id: str = "",
        registry_port: int = 0,
        fileshare_port: int = 0,
    ):
        """Announce this node as the mesh master via mDNS."""
        await self._ensure_zeroconf()

        local_ip = _get_local_ip()
        properties = {
            b"node_id": node_id.encode(),
            b"name": name.encode(),
            b"registry_port": str(registry_port or port).encode(),
            b"fileshare_port": str(fileshare_port).encode(),
            b"version": b"0.1.0",
        }

        self._service_info = ServiceInfo(
            MASTER_SERVICE_TYPE,
            f"{name}.{MASTER_SERVICE_TYPE}",
            addresses=[socket.inet_aton(local_ip)],
            port=port,
            properties=properties,
            server=f"{name}.local.",
        )

        await self._zeroconf.async_register_service(self._service_info)
        logger.info(f"mDNS: Announced master '{name}' at {local_ip}:{port}")

    async def announce_agent(
        self,
        name: str,
        host: str,
        port: int,
        node_id: str = "",
        role: str = "slave",
    ):
        """Announce this node as a mesh agent via mDNS."""
        await self._ensure_zeroconf()

        local_ip = _get_local_ip()
        properties = {
            b"node_id": node_id.encode(),
            b"name": name.encode(),
            b"role": role.encode(),
            b"version": b"0.1.0",
        }

        self._service_info = ServiceInfo(
            AGENT_SERVICE_TYPE,
            f"{name}.{AGENT_SERVICE_TYPE}",
            addresses=[socket.inet_aton(local_ip)],
            port=port,
            properties=properties,
            server=f"{name}.local.",
        )

        await self._zeroconf.async_register_service(self._service_info)
        logger.info(f"mDNS: Announced agent '{name}' at {local_ip}:{port}")

    async def discover_master(self, timeout: float = 10.0) -> MasterInfo | None:
        """Browse the network for a mesh master node.

        Returns the first master found within timeout, or None.
        """
        await self._ensure_zeroconf()

        found: MasterInfo | None = None
        found_event = asyncio.Event()

        class Listener:
            def add_service(self, zc, type_, name):
                nonlocal found
                asyncio.ensure_future(self._resolve(zc, type_, name))

            async def _resolve(self, zc, type_, name):
                nonlocal found
                info = AsyncServiceInfo(type_, name)
                await info.async_request(zc, 3000)
                if info.addresses:
                    host = socket.inet_ntoa(info.addresses[0])
                    props = {
                        k.decode(): v.decode()
                        for k, v in (info.properties or {}).items()
                    }
                    found = MasterInfo(
                        host=host,
                        port=info.port or 9000,
                        node_id=props.get("node_id", ""),
                        name=props.get("name", ""),
                        registry_port=int(props.get("registry_port", "0")),
                        fileshare_port=int(props.get("fileshare_port", "0")),
                    )
                    found_event.set()
                    logger.info(f"mDNS: Discovered master at {host}:{info.port}")

            def remove_service(self, zc, type_, name):
                pass

            def update_service(self, zc, type_, name):
                pass

        listener = Listener()
        browser = AsyncServiceBrowser(
            self._zeroconf.zeroconf, MASTER_SERVICE_TYPE, listener
        )

        try:
            await asyncio.wait_for(found_event.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning(f"mDNS: No master found within {timeout}s")
        finally:
            await browser.async_cancel()

        return found

    async def discover_agents(self, timeout: float = 5.0) -> list[NodeInfo]:
        """Browse for all mesh agents on the network."""
        await self._ensure_zeroconf()

        agents: list[NodeInfo] = []
        done_event = asyncio.Event()

        class Listener:
            def add_service(self, zc, type_, name):
                asyncio.ensure_future(self._resolve(zc, type_, name))

            async def _resolve(self, zc, type_, name):
                info = AsyncServiceInfo(type_, name)
                await info.async_request(zc, 3000)
                if info.addresses:
                    host = socket.inet_ntoa(info.addresses[0])
                    props = {
                        k.decode(): v.decode()
                        for k, v in (info.properties or {}).items()
                    }
                    agents.append(
                        NodeInfo(
                            node_id=props.get("node_id", ""),
                            name=props.get("name", name),
                            host=host,
                            port=info.port or 10000,
                            role=props.get("role", "slave"),
                        )
                    )

            def remove_service(self, zc, type_, name):
                pass

            def update_service(self, zc, type_, name):
                pass

        listener = Listener()
        browser = AsyncServiceBrowser(
            self._zeroconf.zeroconf, AGENT_SERVICE_TYPE, listener
        )

        await asyncio.sleep(timeout)
        await browser.async_cancel()
        return agents

    async def stop(self):
        """Unregister mDNS services and close."""
        if self._service_info and self._zeroconf:
            await self._zeroconf.async_unregister_service(self._service_info)
        if self._zeroconf:
            await self._zeroconf.async_close()
            self._zeroconf = None


def _get_local_ip() -> str:
    """Get this machine's LAN IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"
