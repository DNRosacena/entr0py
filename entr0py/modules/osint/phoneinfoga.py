"""entr0py.modules.osint.phoneinfoga — Phone number recon and OSINT."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class PhoneInfoga(Module):
    meta = ModuleMeta(
        name="PhoneInfoga",
        slug="phoneinfoga",
        description=(
            "Gather information about phone numbers: country, carrier, line type, "
            "and scan for online profiles using OSINT sources."
        ),
        category=Category.OSINT,
        author="sundowndev",
        version="2.x",
        tags=["phone", "osint", "recon"],
        tools=["phoneinfoga"],
        offensive=False,
    )

    def options(self) -> list[Option]:
        return [
            Option("number",  "-n",       "Target phone number in E.164 format (e.g. +14155552671)"),
            Option("disable", "--disable", "Comma-separated scanners to skip (e.g. local,ovh)",
                   required=False, default=""),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = ["phoneinfoga", "scan", "-n", opts["number"]]
        if opts.get("disable"):
            for scanner in opts["disable"].split(","):
                scanner = scanner.strip()
                if scanner:
                    cmd += ["--disable", scanner]
        async for line in self._exec(cmd):
            yield line
