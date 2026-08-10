"""
entr0py.core.playbook
~~~~~~~~~~~~~~~~~~~~~~
Multi-stage tool chains ("playbooks") defined in TOML.

A playbook is an ordered list of stages; each stage runs a module, and its parsed
artifacts (hosts / URLs via ``Module.parse()``) are written to a file and fed into the
next stage's option (declared by ``feed``). Example:

    subfinder(domain) → [hosts] → httpx(-l) → [live URLs] → nuclei(-l)

TOML schema (see ``entr0py/playbooks/recon.toml``):

    name = "recon"
    description = "..."

    [[stage]]
    module  = "subfinder"
    options = { domain = "{target}", all = "true" }

    [[stage]]
    module  = "httpx"
    feed    = "input"                      # previous artifacts → this option (as a file)
    options = { silent = "true", status = "true" }
"""
from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any, AsyncIterator

from entr0py.core.paths import DATA_DIR

# Bundled playbooks ship in the package; users may drop more into DATA_DIR/playbooks.
_PLAYBOOK_DIRS = [
    Path(__file__).resolve().parent.parent / "playbooks",
    DATA_DIR / "playbooks",
]


def _find(name: str) -> Path | None:
    for d in _PLAYBOOK_DIRS:
        p = d / f"{name}.toml"
        if p.exists():
            return p
    return None


def list_playbooks() -> dict[str, dict]:
    """Return {name: parsed_toml} for every discoverable playbook (package first)."""
    found: dict[str, dict] = {}
    for d in _PLAYBOOK_DIRS:
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.toml")):
            if p.stem in found:
                continue
            try:
                found[p.stem] = tomllib.loads(p.read_text())
            except Exception:  # noqa: BLE001 — skip malformed playbooks, don't crash the list
                continue
    return found


def _subst(value: Any, variables: dict[str, str]) -> Any:
    """Replace {var} placeholders in a string option value with CLI-provided vars."""
    if isinstance(value, str):
        for k, v in variables.items():
            value = value.replace("{" + k + "}", v)
    return value


async def run_playbook(
    name: str,
    variables: dict[str, str],
    session_id: int | None = None,
) -> AsyncIterator[str]:
    """Run a playbook end to end, streaming progress + each stage's output."""
    import entr0py.modules  # noqa: F401 — ensure modules are registered
    from entr0py.core.executor import execute
    from entr0py.core.registry import get_registry

    path = _find(name)
    if path is None:
        avail = ", ".join(list_playbooks()) or "none"
        yield f"[!] Unknown playbook: {name!r}. Available: {avail}"
        return

    data = tomllib.loads(path.read_text())
    stages = data.get("stage", [])
    if not stages:
        yield f"[!] Playbook {name!r} has no stages."
        return

    registry = get_registry()
    yield f"[*] Playbook [bold]{data.get('name', name)}[/] — {len(stages)} stage(s)"
    if data.get("description"):
        yield f"    {data['description']}"

    tmp = DATA_DIR / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    prev_artifacts: list[str] = []

    for i, stage in enumerate(stages, 1):
        slug = stage.get("module", "")
        module = registry.get(slug)
        if module is None:
            yield f"[!] Stage {i}: unknown module {slug!r} — aborting."
            return

        opts = {k: _subst(v, variables) for k, v in (stage.get("options") or {}).items()}

        feed = stage.get("feed")
        if feed:
            if not prev_artifacts:
                yield (f"[!] Stage {i} ({slug}) needs input from the previous stage, "
                       f"but it produced 0 artifacts — stopping.")
                return
            feed_file = tmp / f"{name}_stage{i}_in.txt"
            feed_file.write_text("\n".join(prev_artifacts) + "\n")
            opts[feed] = str(feed_file)

        yield ""
        yield f"━━ Stage {i}/{len(stages)}: {module.meta.name} ({slug}) ━━"
        if feed:
            yield f"   ← fed {len(prev_artifacts)} target(s) from the previous stage"

        lines: list[str] = []
        async for line in execute(module, opts, session_id=session_id):
            lines.append(line)
            yield line

        prev_artifacts = module.parse(lines)
        if prev_artifacts:
            yield f"[+] Stage {i} → {len(prev_artifacts)} artifact(s) for the next stage."
        elif i < len(stages):
            yield f"[~] Stage {i} produced no feed-forward artifacts."

    yield ""
    yield "[+] Playbook complete."
