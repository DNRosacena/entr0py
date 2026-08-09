"""entr0py.modules.osint.maigret — Deep username OSINT across 3000+ sites."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Maigret(Module):
    meta = ModuleMeta(
        name="Maigret",
        slug="maigret",
        description=(
            "Username OSINT across 3000+ sites. Builds a full profile: "
            "linked accounts, bios, profile images, and relationship graphs."
        ),
        category=Category.OSINT,
        author="soxoj",
        version="0.4+",
        tags=["username", "osint", "profile", "social-media"],
        packages=["maigret"],
        tools=["maigret"],
        offensive=False,
    )

    def options(self) -> list[Option]:
        return [
            Option("username", "",          "Target username"),
            Option("report",   "--html",    "Generate HTML report",
                   type=OptionType.BOOLEAN, required=False, default=True),
            Option("timeout",  "--timeout", "Per-site timeout (seconds)",
                   type=OptionType.INTEGER, required=False, default=10),
            Option("retries",  "--retries", "Retry count on failure",
                   type=OptionType.INTEGER, required=False, default=1),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = ["maigret", opts["username"]]
        if opts.get("report"):
            cmd.append("--html")
        if opts.get("timeout"):
            cmd += ["--timeout", str(opts["timeout"])]
        if opts.get("retries"):
            cmd += ["--retries", str(opts["retries"])]
        async for line in self._exec(cmd):
            yield line
