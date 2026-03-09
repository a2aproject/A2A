"""CLI entry point for A2A Mesh."""

from __future__ import annotations

import asyncio
import logging
import sys

import click
from rich.console import Console
from rich.table import Table

console = Console()


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable debug logging")
def main(verbose: bool):
    """A2A Mesh — Local agent star network."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


@main.command()
@click.option("--config", "-c", required=True, help="Path to YAML config file")
def start(config: str):
    """Start a mesh node (master or slave agent)."""
    from mesh.agent.config import AgentConfig

    cfg = AgentConfig.from_yaml(config)
    console.print(f"[bold green]Starting[/] {cfg.node.name} ({cfg.node.role})")
    console.print(f"  LLM: {cfg.llm.base_url} / {cfg.llm.model}")
    console.print(f"  Port: {cfg.node.port}")

    if cfg.node.role == "master":
        asyncio.run(_start_master(cfg))
    else:
        asyncio.run(_start_slave(cfg))


async def _start_master(config):
    """Start master node with orchestrator, registry, file share, and UI."""
    from mesh.server import create_master_server

    app = await create_master_server(config)

    import uvicorn

    uv_config = uvicorn.Config(
        app,
        host=config.node.host,
        port=config.node.port,
        log_level="info",
    )
    server = uvicorn.Server(uv_config)
    await server.serve()


async def _start_slave(config):
    """Start slave node with agent server."""
    from mesh.server import create_slave_server

    app = await create_slave_server(config)

    import uvicorn

    uv_config = uvicorn.Config(
        app,
        host=config.node.host,
        port=config.node.port,
        log_level="info",
    )
    server = uvicorn.Server(uv_config)
    await server.serve()


@main.command("agents")
@click.option("--master", "-m", default=None, help="Master URL (auto-discover if not set)")
def list_agents(master: str | None):
    """List all agents in the mesh."""
    asyncio.run(_list_agents(master))


async def _list_agents(master_url: str | None):
    if not master_url:
        console.print("[yellow]Auto-discovering master...[/]")
        from mesh.network.discovery import MeshDiscovery

        discovery = MeshDiscovery()
        master_info = await discovery.discover_master(timeout=5)
        if not master_info:
            console.print("[red]No master node found on network.[/]")
            return
        master_url = f"http://{master_info.host}:{master_info.port}"
        await discovery.stop()

    import httpx

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{master_url}/registry/agents")
            agents = resp.json()
        except Exception as e:
            console.print(f"[red]Failed to reach master: {e}[/]")
            return

    table = Table(title="Mesh Agents")
    table.add_column("Name", style="cyan")
    table.add_column("Role", style="green")
    table.add_column("Status", style="bold")
    table.add_column("LLM", style="yellow")
    table.add_column("URL")
    table.add_column("Skills")

    for agent in agents:
        status = "[green]● Online[/]" if agent.get("healthy") else "[red]● Offline[/]"
        skills = ", ".join(agent.get("skill_tags", []))
        table.add_row(
            agent.get("name", "?"),
            agent.get("role", "?"),
            status,
            agent.get("llm_model", "?"),
            agent.get("url", "?"),
            skills,
        )

    console.print(table)


@main.command()
@click.argument("agent_name")
@click.argument("message")
@click.option("--master", "-m", default=None, help="Master URL")
def send(agent_name: str, message: str, master: str | None):
    """Send a message to an agent."""
    asyncio.run(_send_message(agent_name, message, master))


async def _send_message(agent_name: str, message: str, master_url: str | None):
    console.print(f"[bold]Sending to {agent_name}:[/] {message}")
    # TODO: Implement via A2A client
    console.print("[yellow]Direct message sending not yet implemented. Use the web UI.[/]")


@main.command()
def status():
    """Show mesh cluster status."""
    asyncio.run(_show_status())


async def _show_status():
    console.print("[yellow]Status check not yet implemented. Use: mesh agents --master <url>[/]")


if __name__ == "__main__":
    main()
