"""entr0py.modules.forensics.volatility3 — Memory forensics framework."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Volatility3(Module):
    meta = ModuleMeta(
        name="Volatility 3",
        slug="volatility3",
        description=(
            "Memory forensics framework for analyzing RAM dumps from Windows, Linux, "
            "and macOS. Extract processes, network connections, registry hives, and more."
        ),
        category=Category.FORENSICS,
        author="Volatility Foundation",
        version="2.x",
        tags=["memory", "forensics", "ram", "windows", "linux", "malware"],
        packages=["volatility3"],
        tools=["vol"],
        offensive=False,
    )

    def options(self) -> list[Option]:
        return [
            Option("image",   "-f",  "Memory dump file"),
            Option("plugin",  "",    "Plugin to run (e.g. windows.pslist, linux.bash)",
                   required=False, default="windows.pslist"),
            Option("output",  "--output", "Output format (text|json|csv)",
                   required=False, default="text"),
            Option("pid",     "--pid", "Filter by PID",
                   type=OptionType.INTEGER, required=False, default=0),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = ["vol", "-f", opts["image"], opts.get("plugin", "windows.pslist")]
        cmd += [f"--output={opts.get('output', 'text')}"]
        if opts.get("pid"):
            cmd += ["--pid", str(opts["pid"])]
        async for line in self._exec(cmd):
            yield line
