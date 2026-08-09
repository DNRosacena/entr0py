"""entr0py.modules.osint.sherlock — Username search across 400+ platforms."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Sherlock(Module):
    meta = ModuleMeta(
        name="Sherlock",
        slug="sherlock",
        description="Hunt down social media accounts by username across 400+ sites.",
        category=Category.OSINT,
        author="sherlock-project",
        version="0.15+",
        tags=["username", "social-media", "osint"],
        packages=["sherlock-project"],
        tools=["sherlock"],
        offensive=False,
    )

    def options(self) -> list[Option]:
        return [
            Option("username", "",       "Target username(s), space-separated"),
            Option("output",   "--output", "Output directory",
                   required=False, default="sherlock_out"),
            Option("timeout",  "--timeout", "Timeout per site (seconds)",
                   type=OptionType.INTEGER, required=False, default=15),
            Option("print_found", "--print-found", "Only print found accounts",
                   type=OptionType.BOOLEAN, required=False, default=True),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        usernames = opts["username"].split()
        cmd = ["sherlock"] + usernames
        if opts.get("timeout"):
            cmd += ["--timeout", str(opts["timeout"])]
        if opts.get("print_found"):
            cmd.append("--print-found")
        # --output only supported for a single username
        if opts.get("output") and len(usernames) == 1:
            cmd += ["--output", opts["output"]]
        async for line in self._exec(cmd):
            yield line
