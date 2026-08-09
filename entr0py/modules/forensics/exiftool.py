"""entr0py.modules.forensics.exiftool — Metadata extraction from any file type."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Exiftool(Module):
    meta = ModuleMeta(
        name="ExifTool",
        slug="exiftool",
        description=(
            "Read and write metadata from 100+ file formats including images, PDFs, "
            "Office docs, audio, video. Reveals GPS, device info, author, and timestamps."
        ),
        category=Category.FORENSICS,
        author="Phil Harvey",
        version="12.x",
        tags=["metadata", "exif", "osint", "image", "document", "gps"],
        tools=["exiftool"],
        offensive=False,
    )

    def options(self) -> list[Option]:
        return [
            Option("file",   "",    "Target file or directory"),
            Option("json",   "-json", "Output as JSON",
                   type=OptionType.BOOLEAN, required=False, default=False),
            Option("gps",    "-gps:all", "Extract GPS data only",
                   type=OptionType.BOOLEAN, required=False, default=False),
            Option("remove", "-all=", "Strip all metadata (write mode)",
                   type=OptionType.BOOLEAN, required=False, default=False),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = ["exiftool"]
        if opts.get("json"):
            cmd.append("-json")
        if opts.get("gps"):
            cmd.append("-gps:all")
        if opts.get("remove"):
            cmd.append("-all=")
        cmd.append(opts["file"])
        async for line in self._exec(cmd):
            yield line
