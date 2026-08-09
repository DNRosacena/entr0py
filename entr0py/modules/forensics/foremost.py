"""entr0py.modules.forensics.foremost — File carving from disk images."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Foremost(Module):
    meta = ModuleMeta(
        name="Foremost",
        slug="foremost",
        description=(
            "File carving tool: recover deleted files from disk images or raw data "
            "using header/footer signatures for JPG, PNG, MP4, PDF, ZIP, and more."
        ),
        category=Category.FORENSICS,
        author="Jesse Kornblum",
        version="1.5+",
        tags=["carving", "recovery", "deleted-files", "disk-image", "forensics"],
        tools=["foremost"],
        offensive=False,
    )

    def options(self) -> list[Option]:
        return [
            Option("input",  "-i",  "Input file (disk image or raw device)"),
            Option("output", "-o",  "Output directory",
                   required=False, default="foremost_out"),
            Option("types",  "-t",  "File types to carve (jpg,png,pdf,zip,all)",
                   required=False, default="all"),
            Option("verbose","-v",  "Verbose output",
                   type=OptionType.BOOLEAN, required=False, default=False),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = ["foremost", "-i", opts["input"]]
        if opts.get("output"):
            cmd += ["-o", opts["output"]]
        if opts.get("types"):
            cmd += ["-t", opts["types"]]
        if opts.get("verbose"):
            cmd.append("-v")
        async for line in self._exec(cmd):
            yield line
