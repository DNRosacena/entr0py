"""
entr0py.__main__
~~~~~~~~~~~~~~~~
CLI entry point.  Run `entr0py` for the TUI, or use sub-commands for
headless/scripted operation.

  entr0py                       Launch interactive menu
  entr0py list [--category X]   List modules
  entr0py search <query>         Search modules
  entr0py run <slug> [k=v …]    Run a module (headless)
  entr0py install <slug>         Install a module's dependencies
  entr0py scope add <target>    Add target to active scope
  entr0py scope list             Show current scope
  entr0py session new <name>     Create a new session
  entr0py session list           List sessions
  entr0py report <file> [--fmt]  Generate a report from an output file
"""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

console = Console()
cli     = typer.Typer(
    name="entr0py",
    help="[bold green]entr0py[/] — Modular Penetration Testing Framework",
    rich_markup_mode="rich",
    no_args_is_help=False,
)
scope_cli    = typer.Typer(help="Manage target scope")
session_cli  = typer.Typer(help="Manage scan sessions")
playbook_cli = typer.Typer(help="Run multi-stage tool chains (playbooks)")
cli.add_typer(scope_cli,    name="scope")
cli.add_typer(session_cli,  name="session")
cli.add_typer(playbook_cli, name="playbook")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_registry():
    import entr0py.modules  # noqa: F401 — registers all modules
    from entr0py.core.registry import get_registry
    return get_registry()


def _banner() -> None:
    from entr0py.ui.menu import _BANNER
    console.print(f"[bold green]{_BANNER}[/]")
    console.print("[dim]  Modular Penetration Testing Framework[/]\n")


# ---------------------------------------------------------------------------
# Root command — launch TUI
# ---------------------------------------------------------------------------

@cli.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """Launch the entr0py TUI.  Run a sub-command for headless operation."""
    if ctx.invoked_subcommand is None:
        from entr0py.ui.menu import main_menu
        main_menu()


# ---------------------------------------------------------------------------
# entr0py list
# ---------------------------------------------------------------------------

@cli.command("list")
def cmd_list(
    category: Optional[str] = typer.Option(None, "--category", "-c",
                                            help="Filter by category slug"),
    installed_only: bool = typer.Option(False, "--installed", "-i",
                                        help="Only show installed modules"),
) -> None:
    """List all available modules."""
    _banner()
    registry = _load_registry()
    modules  = registry.all()

    if category:
        from entr0py.core.base import Category
        try:
            cat     = Category(category.lower())
            modules = registry.by_category(cat)
        except ValueError:
            console.print(f"[red]Unknown category: {category}[/]")
            raise typer.Exit(1)

    if installed_only:
        modules = [m for m in modules if m.is_installed()]

    t = Table(show_header=True, header_style="bold green")
    t.add_column("Slug",        style="cyan",   no_wrap=True)
    t.add_column("Name",        style="bold")
    t.add_column("Category")
    t.add_column("Installed",   justify="center")
    t.add_column("Description", max_width=55)

    for m in sorted(modules, key=lambda x: (x.meta.category.value, x.meta.slug)):
        t.add_row(
            m.meta.slug,
            m.meta.name,
            m.meta.category.label,
            "[green]✓[/]" if m.is_installed() else "[red]✗[/]",
            m.meta.description[:55],
        )

    console.print(t)
    console.print(f"\n[dim]{len(modules)} modules[/]")


# ---------------------------------------------------------------------------
# entr0py search
# ---------------------------------------------------------------------------

@cli.command("search")
def cmd_search(query: str = typer.Argument(..., help="Search term")) -> None:
    """Search modules by name, tag, or description."""
    registry = _load_registry()
    results  = registry.search(query)
    if not results:
        console.print(f"[yellow]No modules found for: {query!r}[/]")
        return
    console.print(f"[green]{len(results)} result(s) for [bold]{query!r}[/bold][/]\n")
    for m in results:
        status = "[green]●[/]" if m.is_installed() else "[red]○[/]"
        console.print(f"  {status} [cyan]{m.meta.slug:<20}[/] {m.meta.name} — {m.meta.description[:60]}")


# ---------------------------------------------------------------------------
# entr0py run
# ---------------------------------------------------------------------------

@cli.command("run")
def cmd_run(
    slug: str = typer.Argument(..., help="Module slug (e.g. subfinder)"),
    opts: list[str] = typer.Argument(default=[], help="key=value options"),
    session_id: Optional[int] = typer.Option(None, "--session", "-s"),
) -> None:
    """Run a module headlessly.  Pass options as key=value pairs."""
    registry = _load_registry()
    module   = registry.get(slug)
    if module is None:
        console.print(f"[red]Unknown module: {slug!r}. Run `entr0py list` to see all modules.[/]")
        raise typer.Exit(1)

    # Parse key=value opts
    parsed: dict = {}
    for item in opts:
        if "=" in item:
            k, _, v = item.partition("=")
            parsed[k.strip()] = v.strip()
        else:
            console.print(f"[yellow]Skipping malformed option: {item!r} (expected key=value)[/]")

    async def _run() -> None:
        from entr0py.core.executor import execute
        async for line in execute(module, parsed, session_id=session_id):
            console.print(line)

    asyncio.run(_run())


# ---------------------------------------------------------------------------
# entr0py install
# ---------------------------------------------------------------------------

@cli.command("install")
def cmd_install(slug: str = typer.Argument(..., help="Module slug to install")) -> None:
    """Install a module's dependencies."""
    registry = _load_registry()
    module   = registry.get(slug)
    if module is None:
        console.print(f"[red]Unknown module: {slug!r}[/]")
        raise typer.Exit(1)

    async def _install() -> None:
        from entr0py.core.installer import install_module
        async for line in install_module(module):
            console.print(line)

    asyncio.run(_install())


# ---------------------------------------------------------------------------
# entr0py scope
# ---------------------------------------------------------------------------

@scope_cli.command("add")
def scope_add(targets: list[str] = typer.Argument(..., help="IP, CIDR, or domain")) -> None:
    """Add target(s) to the active scope."""
    from entr0py.core.scope import active
    for t in targets:
        active().add(t)
        console.print(f"[green][+] Added to scope: {t}[/]")
    console.print(f"[dim]Scope: {active().entries()}[/]")


@scope_cli.command("list")
def scope_list() -> None:
    """Show the current active scope."""
    from entr0py.core.scope import active
    entries = active().entries()
    if not entries:
        console.print("[yellow]Scope is empty.[/]")
    else:
        for e in entries:
            console.print(f"  [cyan]{e}[/]")


@scope_cli.command("clear")
def scope_clear() -> None:
    """Clear all scope entries."""
    from entr0py.core import scope as scope_mod
    scope_mod.reset()
    console.print("[green]Scope cleared.[/]")


# ---------------------------------------------------------------------------
# entr0py session
# ---------------------------------------------------------------------------

@session_cli.command("new")
def session_new(
    name: str = typer.Argument(..., help="Session name"),
    scope: Optional[str] = typer.Option(None, "--scope", "-s",
                                        help="Comma-separated scope entries"),
) -> None:
    """Create a new scan session."""
    scope_list = [s.strip() for s in scope.split(",") if s.strip()] if scope else []

    async def _create() -> None:
        import entr0py.core.session as sess
        sid = await sess.create_session(name, scope_list)
        console.print(f"[green][+] Session created: #{sid} — {name}[/]")
        if scope_list:
            console.print(f"[dim]    Scope: {scope_list}[/]")

    asyncio.run(_create())


@session_cli.command("list")
def session_list() -> None:
    """List all past sessions."""
    import json

    async def _list() -> None:
        import entr0py.core.session as sess
        sessions = await sess.list_sessions()
        if not sessions:
            console.print("[yellow]No sessions found.[/]")
            return
        t = Table(show_header=True, header_style="bold green")
        t.add_column("ID",      style="cyan", justify="right")
        t.add_column("Name",    style="bold")
        t.add_column("Created", style="dim")
        t.add_column("Scope")
        for s in sessions:
            scope = json.loads(s["scope_json"])
            t.add_row(str(s["id"]), s["name"], s["created_at"][:19],
                      ", ".join(scope) or "[dim]none[/dim]")
        console.print(t)

    asyncio.run(_list())


# ---------------------------------------------------------------------------
# entr0py playbook
# ---------------------------------------------------------------------------

@playbook_cli.command("list")
def playbook_list() -> None:
    """List available playbooks (multi-stage tool chains)."""
    from entr0py.core.playbook import list_playbooks
    pbs = list_playbooks()
    if not pbs:
        console.print("[yellow]No playbooks found.[/]")
        return
    for pname, data in pbs.items():
        chain = " [bright_black]→[/] ".join(
            s.get("module", "?") for s in data.get("stage", [])
        )
        console.print(f"  [cyan]{pname}[/] — {data.get('description', '')}")
        console.print(f"      [dim]{chain}[/]")


@playbook_cli.command("run")
def playbook_run(
    name: str = typer.Argument(..., help="Playbook name (e.g. recon)"),
    opts: list[str] = typer.Argument(default=[], help="key=value vars (e.g. target=example.com)"),
    session_id: Optional[int] = typer.Option(None, "--session", "-s"),
) -> None:
    """Run a playbook, passing key=value vars (substituted into {placeholders})."""
    variables: dict = {}
    for item in opts:
        if "=" in item:
            k, _, v = item.partition("=")
            variables[k.strip()] = v.strip()
        else:
            console.print(f"[yellow]Skipping malformed var: {item!r} (expected key=value)[/]")

    async def _run() -> None:
        from entr0py.core.playbook import run_playbook
        async for line in run_playbook(name, variables, session_id=session_id):
            console.print(line)

    asyncio.run(_run())


# ---------------------------------------------------------------------------
# entr0py wordlists
# ---------------------------------------------------------------------------

@cli.command("wordlists")
def cmd_wordlists(
    slug: Optional[str] = typer.Argument(None, help="Wordlist slug to download (omit for list)"),
    all_: bool = typer.Option(False, "--all", "-a", help="Download all wordlists"),
    list_: bool = typer.Option(False, "--list", "-l", help="List available wordlists"),
) -> None:
    """Manage wordlists — list, download, or show paths."""
    from entr0py.core import wordlists as wl_mod
    from rich.table import Table as RTable

    if list_ or (not slug and not all_):
        t = RTable(show_header=True, header_style="bold green")
        t.add_column("Slug",        style="cyan",  no_wrap=True)
        t.add_column("Name",        style="bold")
        t.add_column("Category")
        t.add_column("Size",        justify="right")
        t.add_column("Status",      justify="center")
        t.add_column("Path")
        for w in wl_mod.REGISTRY:
            p      = wl_mod.path(w.slug)
            status = "[green]✓[/]" if p else "[red]✗[/]"
            size   = f"{w.size_mb:.0f} MB" if w.size_mb >= 1 else f"{w.size_mb*1000:.0f} KB"
            t.add_row(w.slug, w.name, w.category, size, status, str(p or ""))
        console.print(t)
        return

    async def _dl() -> None:
        if all_:
            async for line in wl_mod.download_all():
                console.print(line)
        elif slug:
            async for line in wl_mod.download(slug):
                console.print(line)

    asyncio.run(_dl())


# ---------------------------------------------------------------------------
# entr0py report
# ---------------------------------------------------------------------------

@cli.command("report")
def cmd_report(
    file: Path = typer.Argument(..., help="Output file to generate report from"),
    fmt: str   = typer.Option("json", "--fmt", "-f", help="Report format: json | html"),
) -> None:
    """Generate a report from a saved output file."""
    if not file.exists():
        console.print(f"[red]File not found: {file}[/]")
        raise typer.Exit(1)
    from entr0py.utils.reporter import report_from_file
    out = report_from_file(file, fmt=fmt)
    console.print(f"[green][+] Report saved to: {out}[/]")


# ---------------------------------------------------------------------------

def main_entry() -> None:
    from entr0py.core.paths import setup_env
    setup_env()
    cli()


if __name__ == "__main__":
    main_entry()
