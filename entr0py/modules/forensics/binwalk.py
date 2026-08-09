"""entr0py.modules.forensics.binwalk — Firmware and binary analysis."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Binwalk(Module):
    meta = ModuleMeta(
        name="Binwalk",
        slug="binwalk",
        description=(
            "Firmware analysis tool: scan for embedded files and executable code, "
            "extract filesystems, and identify compression/encryption."
        ),
        category=Category.FORENSICS,
        author="ReFirmLabs",
        version="2.3+",
        tags=["firmware", "binary", "extract", "carving", "embedded"],
        tools=["binwalk"],
        offensive=False,
    )

    def options(self) -> list[Option]:
        return [
            Option("file",    "",    "Target binary/firmware file"),
            Option("extract", "-e",  "Automatically extract files",
                   type=OptionType.BOOLEAN, required=False, default=True),
            Option("entropy", "-E",  "Plot file entropy",
                   type=OptionType.BOOLEAN, required=False, default=False),
            Option("matryoshka", "-M", "Recursively extract (matryoshka mode)",
                   type=OptionType.BOOLEAN, required=False, default=False),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = ["binwalk", opts["file"]]
        if opts.get("extract", True):
            cmd.append("-e")
        if opts.get("entropy"):
            cmd.append("-E")
        if opts.get("matryoshka"):
            cmd.append("-M")
        async for line in self._exec(cmd):
            yield line
