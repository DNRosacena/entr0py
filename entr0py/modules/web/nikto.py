"""entr0py.modules.web.nikto — Web server scanner for misconfigs and vulnerabilities."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Nikto(Module):
    meta = ModuleMeta(
        name="Nikto",
        slug="nikto",
        description=(
            "Open-source web server scanner: checks 6700+ dangerous files/programs, "
            "outdated server versions, version-specific problems, and misconfigurations."
        ),
        category=Category.WEB,
        author="sullo",
        version="2.x",
        tags=["web-scan", "misconfig", "server", "cgi"],
        tools=["nikto"],
    )

    def options(self) -> list[Option]:
        return [
            Option("host",    "-h",      "Target host or URL"),
            Option("port",    "-p",      "Port (default: 80 or 443 for SSL)",
                   type=OptionType.INTEGER, required=False, default=80),
            Option("ssl",     "-ssl",    "Force SSL",
                   type=OptionType.BOOLEAN, required=False, default=False),
            Option("output",  "-o",      "Output file",
                   required=False, default="nikto_out.html"),
            Option("format",  "-Format", "Output format (csv|html|nbe|xml|txt)",
                   required=False, default="html"),
            Option("tuning",  "-Tuning", "Scan tuning (1-9, x,b,g,…)",
                   required=False, default=""),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = ["nikto", "-h", opts["host"], "-p", str(opts.get("port", 80))]
        if opts.get("ssl"):
            cmd.append("-ssl")
        if opts.get("output"):
            cmd += ["-o", opts["output"], "-Format", opts.get("format", "html")]
        if opts.get("tuning"):
            cmd += ["-Tuning", opts["tuning"]]
        async for line in self._exec(cmd):
            yield line
