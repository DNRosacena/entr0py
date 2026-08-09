"""
entr0py.core.executor
~~~~~~~~~~~~~~~~~~~~~
Runs a module, enforces scope, persists the run to the session DB,
and streams output to an async queue that callers can read.

Usage (CLI / TUI):
------------------
    async for line in execute(module, opts, session_id=1):
        print(line)
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, AsyncIterator

from entr0py.core import scope as scope_mod
from entr0py.core import session as session_mod
from entr0py.core.paths import OUTPUT_DIR
from entr0py.core.base import Module
from entr0py.core.config import get as get_cfg


async def execute(
    module: Module,
    opts: dict[str, Any],
    session_id: int | None = None,
    target_key: str = "target",           # which opts key holds the primary target
) -> AsyncIterator[str]:
    """
    Stream output lines from a module run.
    - Checks scope if module.meta.offensive is True and a target is present.
    - Records the run in the session DB if session_id is provided.
    - Writes output to ~/.entr0py/output/<slug>_<run_id>.txt alongside streaming.
    """
    cfg = get_cfg()

    # ------------------------------------------------------------------ scope
    if module.meta.offensive:
        primary_target = opts.get(target_key) or opts.get("domain") or opts.get("url")
        if primary_target:
            try:
                scope_mod.active().check(str(primary_target))
            except scope_mod.ScopeViolation as exc:
                yield str(exc)
                return

    # ------------------------------------------------------------------ session
    run_id: int | None = None
    if session_id is not None:
        run_id = await session_mod.start_run(session_id, module.meta.slug, opts)

    # ------------------------------------------------------------------ output file
    output_dir = OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = f"_{run_id}" if run_id else ""
    out_path = output_dir / f"{module.meta.slug}{suffix}.txt"

    status = "completed"
    try:
        with out_path.open("w", encoding="utf-8") as fh:
            async for line in module.run(opts):
                fh.write(line + "\n")
                yield line
    except Exception as exc:
        status = "failed"
        yield f"[!] Executor error: {exc}"
    finally:
        if run_id is not None:
            await session_mod.finish_run(run_id, status, str(out_path))
