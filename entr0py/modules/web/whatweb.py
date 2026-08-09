"""entr0py.modules.web.whatweb — Web technology fingerprinting."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class WhatWeb(Module):
    meta = ModuleMeta(
        name="WhatWeb",
        slug="whatweb",
        description=(
            "Identify web technologies: CMS, frameworks, JS libraries, server software, "
            "analytics platforms, and 1800+ other plugins."
        ),
        category=Category.WEB,
        author="urbanadventurer",
        version="0.5+",
        tags=["fingerprint", "tech-detect", "cms", "framework", "recon"],
        tools=["whatweb"],
    )

    def options(self) -> list[Option]:
        return [
            Option("target",      "",         "Target URL or IP range"),
            Option("aggression",  "-a",       "Aggression level 1-4 (1=stealthy, 4=heavy)",
                   type=OptionType.INTEGER, required=False, default=1),
            Option("output",      "-o",       "Output file (JSON)",
                   required=False, default="whatweb_out.json"),
            Option("log_verbose", "--log-verbose", "Log verbose to file",
                   required=False, default=""),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        # WhatWeb wants `--aggression=N` (or `-a N`); the old `-a=N` form is parsed
        # as the literal value "=N" and rejected. Valid levels are 1, 3, 4 — there is
        # no level 2 — so normalize anything else to 1 (stealthy).
        level = str(opts.get("aggression", 1)).strip()
        if level not in {"1", "3", "4"}:
            level = "1"
        cmd = ["whatweb", f"--aggression={level}", opts["target"]]
        if opts.get("output"):
            cmd += [f"--log-json={opts['output']}"]
        if opts.get("log_verbose"):
            cmd += [f"--log-verbose={opts['log_verbose']}"]
        async for line in self._exec(cmd):
            yield line
