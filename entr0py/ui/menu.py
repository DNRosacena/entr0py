"""
entr0py.ui.menu
~~~~~~~~~~~~~~~
Airgeddon-style terminal menu.
  - Clear screen per view
  - pyfiglet banner (clean ASCII, works with any monospace font)
  - Numbered categories → numbered modules → option prompts → live output
  - Breadcrumb trail in the prompt line
"""
from __future__ import annotations

import asyncio
import os
import sys
from typing import Any

from rich.console import Console

from entr0py.core.base import Category, Module, OptionType
from entr0py.core.registry import get_registry
from entr0py.__version__ import __version__

console = Console(highlight=False)

# ── Banner ────────────────────────────────────────────────────────────────────

def _make_banner() -> str:
    try:
        import pyfiglet
        return pyfiglet.figlet_format("entr0py", font="slant")
    except Exception:
        return "  entr0py\n"

_BANNER = _make_banner()

# ── Helpers ───────────────────────────────────────────────────────────────────

def _clr() -> None:
    os.system("cls" if os.name == "nt" else "clear")

def _div() -> None:
    console.print("  [bright_black]" + "─" * 62 + "[/bright_black]")

def _ok(msg: str)   -> None: console.print(f"  [bold green][+][/bold green] {msg}")
def _warn(msg: str) -> None: console.print(f"  [bold yellow][*][/bold yellow] {msg}")
def _err(msg: str)  -> None: console.print(f"  [bold red][!][/bold red] {msg}")
def _info(msg: str) -> None: console.print(f"  [bright_black][~] {msg}[/bright_black]")


def _header(breadcrumb: list[str]) -> None:
    console.print(f"[bold green]{_BANNER}[/bold green]", end="")
    r = get_registry()
    installed = len(r.installed())
    total = len(r)
    console.print(
        f"  [bright_black]v{__version__}  ·  "
        f"[/bright_black][green]{installed}[/green]"
        f"[bright_black]/{total} modules installed[/bright_black]"
    )
    if len(breadcrumb) > 1:
        trail = " [bright_black]>[/bright_black] ".join(
            f"[cyan]{b}[/cyan]" for b in breadcrumb
        )
        console.print(f"  {trail}")
    _div()
    console.print()


def _input(breadcrumb: list[str]) -> str:
    trail = " > ".join(breadcrumb)
    return console.input(
        f"\n  [bold green]{trail}[/bold green] [bright_black]>[/bright_black] "
    ).strip()


# ── Screens ───────────────────────────────────────────────────────────────────

def main_menu() -> None:
    """Entry point — loops until quit."""
    import entr0py.modules  # noqa: F401 — registers all modules
    registry = get_registry()
    cats = list(Category)

    while True:
        _clr()
        _header(["entr0py"])
        console.print("  [bold cyan]SELECT CATEGORY[/bold cyan]\n")

        for i, cat in enumerate(cats, 1):
            mods = registry.by_category(cat)
            inst = sum(1 for m in mods if m.is_installed())
            console.print(
                f"  [bold green][{i:>2}][/bold green]  "
                f"[cyan]{cat.label:<26}[/cyan]  "
                f"[green]{inst}[/green][bright_black]/{len(mods)} installed[/bright_black]"
            )

        console.print()
        _div()
        console.print(
            "  [bright_black][[/bright_black][white]s[/white][bright_black]][/bright_black] Search   "
            "[bright_black][[/bright_black][white]w[/white][bright_black]][/bright_black] Wordlists   "
            "[bright_black][[/bright_black][white]x[/white][bright_black]][/bright_black] New Session   "
            "[bright_black][[/bright_black][white]q[/white][bright_black]][/bright_black] Quit"
        )

        choice = _input(["entr0py"])

        if choice.lower() == "q":
            _clr()
            console.print("\n  [bold green]Later.[/bold green]\n")
            sys.exit(0)
        elif choice.lower() == "s":
            search_menu()
        elif choice.lower() == "w":
            wordlists_menu()
        elif choice.lower() == "x":
            session_menu()
        elif choice.isdigit() and 1 <= int(choice) <= len(cats):
            category_menu(cats[int(choice) - 1])


def category_menu(cat: Category) -> None:
    registry = get_registry()

    while True:
        mods = sorted(registry.by_category(cat), key=lambda m: m.meta.name)
        _clr()
        _header(["entr0py", cat.label])
        console.print(f"  [bold cyan]{cat.label.upper()}[/bold cyan]\n")

        for i, m in enumerate(mods, 1):
            dot = "[bold green]●[/bold green]" if m.is_installed() else "[bold red]○[/bold red]"
            replaces = (
                f"  [yellow](replaces: {', '.join(m.meta.replaces)})[/yellow]"
                if m.meta.replaces else ""
            )
            console.print(
                f"  [bold green][{i:>2}][/bold green]  {dot}  "
                f"[bold white]{m.meta.slug:<22}[/bold white]"
                f"[bright_black]{m.meta.description[:44]}[/bright_black]{replaces}"
            )

        console.print()
        _div()
        console.print(
            "  [bright_black][[/bright_black][white]b[/white][bright_black]][/bright_black] Back   "
            "[bright_black][[/bright_black][white]i[/white][bright_black]] [/bright_black]"
            "[bright_black]<n>[/bright_black] Install   "
            "[bright_black][[/bright_black][white]q[/white][bright_black]][/bright_black] Quit"
        )

        choice = _input(["entr0py", cat.label])

        if choice.lower() in ("b", ""):
            return
        elif choice.lower() == "q":
            sys.exit(0)
        elif choice.lower().startswith("i "):
            parts = choice.split()
            if len(parts) == 2 and parts[1].isdigit():
                idx = int(parts[1]) - 1
                if 0 <= idx < len(mods):
                    install_screen(mods[idx])
        elif choice.isdigit() and 1 <= int(choice) <= len(mods):
            module_menu(mods[int(choice) - 1])


def module_menu(module: Module) -> None:
    while True:
        _clr()
        bc = ["entr0py", module.meta.category.label, module.meta.slug]
        _header(bc)

        status = (
            "[bold green]● INSTALLED[/bold green]"
            if module.is_installed()
            else "[bold red]○ NOT INSTALLED[/bold red]  [bright_black](run [i] to install)[/bright_black]"
        )
        console.print(f"  [bold white]{module.meta.name}[/bold white]  {status}")
        console.print(f"  [bright_black]{module.meta.description}[/bright_black]")
        console.print(
            f"  [bright_black]Author: {module.meta.author}   v{module.meta.version}[/bright_black]"
        )
        if module.meta.tags:
            console.print(
                f"  [bright_black]Tags: {' '.join('#' + t for t in module.meta.tags)}[/bright_black]"
            )
        if module.meta.replaces:
            console.print(
                f"  [yellow]Replaces: {', '.join(module.meta.replaces)}[/yellow]"
            )

        options = module.options()
        opts: dict[str, Any] = {}

        if options:
            console.print()
            _div()
            console.print("  [bold cyan]OPTIONS[/bold cyan]\n")

            for opt in options:
                req = "[bold red]*[/bold red]" if opt.required else "[bright_black]?[/bright_black]"
                dflt = (
                    f"  [bright_black](default: {opt.default})[/bright_black]"
                    if opt.default is not None else ""
                )
                console.print(f"  {req} [cyan]{opt.name}[/cyan]{dflt}")
                console.print(f"    [bright_black]{opt.description}[/bright_black]")

                if opt.type == OptionType.BOOLEAN:
                    hint = "Y/n" if opt.default else "y/N"
                    raw = console.input(f"    [yellow]>[/yellow] [{hint}] ").strip().lower()
                    opts[opt.name] = (raw in ("y", "yes", "1")) if raw else bool(opt.default)

                elif opt.type == OptionType.CHOICE and opt.choices:
                    for ci, ch in enumerate(opt.choices, 1):
                        console.print(f"      [bright_black][{ci}][/bright_black] {ch}")
                    raw = console.input("    [yellow]>[/yellow] ").strip()
                    if raw.isdigit() and 1 <= int(raw) <= len(opt.choices):
                        opts[opt.name] = opt.choices[int(raw) - 1]
                    else:
                        opts[opt.name] = raw or opt.default

                else:
                    raw = console.input("    [yellow]>[/yellow] ").strip()
                    if not raw and opt.default is not None:
                        raw = str(opt.default)
                    if opt.type == OptionType.INTEGER:
                        opts[opt.name] = int(raw) if raw and raw.lstrip("-").isdigit() else (opt.default or 0)
                    else:
                        opts[opt.name] = raw

                console.print()

        _div()
        console.print(
            "  [bright_black][[/bright_black][white]r[/white][bright_black]][/bright_black] Run   "
            "[bright_black][[/bright_black][white]i[/white][bright_black]][/bright_black] Install   "
            "[bright_black][[/bright_black][white]b[/white][bright_black]][/bright_black] Back   "
            "[bright_black][[/bright_black][white]q[/white][bright_black]][/bright_black] Quit"
        )
        choice = _input(["entr0py", module.meta.slug]).lower()

        if choice == "q":
            sys.exit(0)
        elif choice == "b":
            return
        elif choice == "i":
            install_screen(module)
        elif choice in ("r", ""):
            if not module.is_installed():
                _warn(f"[bold]{module.meta.name}[/bold] does not appear to be installed.")
                ans = console.input("  [yellow]Install now?[/yellow] [Y/n] ").strip().lower()
                if ans in ("", "y", "yes"):
                    install_screen(module)
                    if not module.is_installed():
                        _err("Installation may have failed. Check output above.")
                        console.input("  Press Enter to continue...")
                        continue
                else:
                    continue
            missing = [o.name for o in options if o.required and not opts.get(o.name)]
            if missing:
                _err(f"Required options missing: {', '.join(missing)}")
                console.input("  Press Enter to retry...")
                continue
            run_screen(module, opts)
            return


def run_screen(module: Module, opts: dict[str, Any]) -> None:
    _clr()
    _header(["entr0py", module.meta.slug, "running"])
    _ok(f"[bold]{module.meta.name}[/bold]  starting…")
    if opts:
        _info("  ".join(f"{k}={v}" for k, v in opts.items() if v not in (None, "", 0, False)))
    _div()
    console.print()

    try:
        asyncio.run(_do_run(module, opts))
    except KeyboardInterrupt:
        console.print()
        _warn("Interrupted by user.")

    _div()
    console.input("\n  [bright_black]Press Enter to continue...[/bright_black]")


async def _do_run(module: Module, opts: dict[str, Any]) -> None:
    from entr0py.core.executor import execute
    async for line in execute(module, opts):
        if line.startswith("[+]"):
            console.print(f"  [bold green]{line}[/bold green]")
        elif line.startswith("[!]"):
            console.print(f"  [bold red]{line}[/bold red]")
        elif line.startswith("[*]"):
            console.print(f"  [bold yellow]{line}[/bold yellow]")
        else:
            console.print(f"  {line}")


def install_screen(module: Module) -> None:
    _clr()
    _header(["entr0py", module.meta.slug, "install"])
    _warn(f"Installing [bold]{module.meta.name}[/bold]…")
    _div()
    console.print()

    try:
        asyncio.run(_do_install(module))
    except KeyboardInterrupt:
        _warn("Interrupted.")

    _div()
    console.input("\n  [bright_black]Press Enter to continue...[/bright_black]")


async def _do_install(module: Module) -> None:
    from entr0py.core.installer import install_module
    async for line in install_module(module):
        if line.startswith("[+]"):
            console.print(f"  [bold green]{line}[/bold green]")
        elif line.startswith("[!]"):
            console.print(f"  [bold red]{line}[/bold red]")
        else:
            console.print(f"  [yellow]{line}[/yellow]")


def search_menu() -> None:
    _clr()
    _header(["entr0py", "search"])
    query = console.input("  [yellow]Search:[/yellow] ").strip()
    if not query:
        return

    registry = get_registry()
    results = registry.search(query)

    _clr()
    _header(["entr0py", "search"])

    if not results:
        _warn(f"No results for: [bold]{query}[/bold]")
        console.input("  Press Enter to continue...")
        return

    _ok(f"{len(results)} result(s) for: [bold]{query}[/bold]")
    console.print()

    for i, m in enumerate(results, 1):
        dot = "[bold green]●[/bold green]" if m.is_installed() else "[bold red]○[/bold red]"
        console.print(
            f"  [bold green][{i:>2}][/bold green]  {dot}  "
            f"[bold white]{m.meta.slug:<22}[/bold white]"
            f"[bright_black]{m.meta.description[:48]}[/bright_black]"
        )

    _div()
    choice = _input(["entr0py", "search"])
    if choice.isdigit() and 1 <= int(choice) <= len(results):
        module_menu(results[int(choice) - 1])


def session_menu() -> None:
    _clr()
    _header(["entr0py", "session"])
    console.print("  [bold cyan]NEW SESSION[/bold cyan]\n")

    name = console.input(
        "  [yellow]Session name[/yellow] [bright_black](Enter to skip):[/bright_black] "
    ).strip() or "unnamed"
    scope = console.input(
        "  [yellow]Scope[/yellow] [bright_black](comma-separated IPs/CIDRs/domains, or blank):[/bright_black] "
    ).strip()

    scope_list = [s.strip() for s in scope.split(",") if s.strip()]

    import entr0py.core.session as sess_mod
    import entr0py.core.scope as scope_mod

    sid = asyncio.run(sess_mod.create_session(name, scope_list))

    scope_mod.reset()
    for entry in scope_list:
        scope_mod.active().add(entry)

    console.print()
    _ok(f"Session [bold]#{sid} — {name}[/bold] created.")
    if scope_list:
        _info(f"Scope: {', '.join(scope_list)}")
    else:
        _warn("No scope defined. Offensive modules will warn before running.")

    console.input("\n  [bright_black]Press Enter to continue...[/bright_black]")


# ── Wordlists ─────────────────────────────────────────────────────────────────

def wordlists_menu() -> None:
    from entr0py.core import wordlists as wl_mod

    cats = wl_mod.categories()

    while True:
        _clr()
        _header(["entr0py", "wordlists"])
        console.print("  [bold cyan]WORDLISTS[/bold cyan]\n")

        all_wls = wl_mod.REGISTRY
        dl = sum(1 for w in all_wls if wl_mod.is_downloaded(w.slug))
        console.print(
            f"  [bright_black]Stored in:[/bright_black] [cyan]{wl_mod.WORDLISTS_DIR}[/cyan]"
        )
        console.print(
            f"  [bright_black]Downloaded:[/bright_black] "
            f"[green]{dl}[/green][bright_black]/{len(all_wls)}[/bright_black]\n"
        )

        idx = 1
        num_map: dict[int, str] = {}
        for cat in cats:
            wls = wl_mod.by_category(cat)
            console.print(f"  [bold yellow]{cat.upper()}[/bold yellow]")
            for w in wls:
                dot  = "[bold green]●[/bold green]" if wl_mod.is_downloaded(w.slug) else "[bold red]○[/bold red]"
                size = (
                    f"[bright_black]{w.size_mb:.0f} MB[/bright_black]"
                    if w.size_mb >= 1
                    else f"[bright_black]{w.size_mb * 1000:.0f} KB[/bright_black]"
                )
                p         = wl_mod.path(w.slug)
                path_hint = f"  [bright_black]{p}[/bright_black]" if p else ""
                console.print(
                    f"  [bold green][{idx:>2}][/bold green]  {dot}  "
                    f"[white]{w.name:<32}[/white]{size}{path_hint}"
                )
                num_map[idx] = w.slug
                idx += 1
            console.print()

        _div()
        console.print(
            "  [bright_black]Enter number to download  "
            "[[/bright_black][white]a[/white][bright_black]] Download all  "
            "[[/bright_black][white]b[/white][bright_black]] Back  "
            "[[/bright_black][white]q[/white][bright_black]][/bright_black] Quit"
        )

        choice = _input(["entr0py", "wordlists"])

        if choice.lower() == "q":
            sys.exit(0)
        elif choice.lower() == "b":
            return
        elif choice.lower() == "a":
            _wordlist_dl_screen(None)
        elif choice.isdigit() and int(choice) in num_map:
            _wordlist_dl_screen(num_map[int(choice)])


def _wordlist_dl_screen(slug: str | None) -> None:
    from entr0py.core import wordlists as wl_mod

    _clr()
    _header(["entr0py", "wordlists", slug or "all"])

    if slug:
        wl = next((w for w in wl_mod.REGISTRY if w.slug == slug), None)
        if not wl:
            _err(f"Unknown wordlist: {slug}")
            console.input("  Press Enter...")
            return
        _warn(f"Downloading: [bold]{wl.name}[/bold]  ({wl.size_mb:.1f} MB)")
    else:
        total_mb = sum(w.size_mb for w in wl_mod.REGISTRY if not wl_mod.is_downloaded(w.slug))
        _warn(f"Downloading all missing wordlists  (~{total_mb:.0f} MB)")

    _div()
    console.print()

    try:
        asyncio.run(_do_wl_download(slug))
    except KeyboardInterrupt:
        _warn("Interrupted.")

    _div()
    console.input("\n  [bright_black]Press Enter to continue...[/bright_black]")


async def _do_wl_download(slug: str | None) -> None:
    from entr0py.core import wordlists as wl_mod
    gen = wl_mod.download(slug) if slug else wl_mod.download_all()
    async for line in gen:
        if line.startswith("[+]"):
            console.print(f"  [bold green]{line}[/bold green]")
        elif line.startswith("[!]"):
            console.print(f"  [bold red]{line}[/bold red]")
        elif line.startswith("[*]"):
            console.print(f"  [bold yellow]{line}[/bold yellow]")
        else:
            console.print(f"  [bright_black]{line}[/bright_black]")
