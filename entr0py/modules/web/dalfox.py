"""entr0py.modules.web.dalfox — Parameter analysis and XSS scanning."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Dalfox(Module):
    meta = ModuleMeta(
        name="Dalfox",
        slug="dalfox",
        description=(
            "Fast parameter analysis and XSS scanner. Handles DOM XSS, blind XSS, "
            "and custom payload injection with automation-friendly output."
        ),
        category=Category.WEB,
        author="hahwul",
        version="2.x",
        tags=["xss", "parameter", "dom-xss", "blind-xss", "injection"],
        tools=["dalfox"],
    )

    def options(self) -> list[Option]:
        return [
            Option("url",     "",         "Target URL"),
            Option("mode",    "",         "Scan mode: url | pipe | file | server",
                   type=OptionType.CHOICE,
                   choices=["url", "pipe", "file", "server"],
                   required=False, default="url"),
            Option("blind",   "--blind",  "Blind XSS callback URL",
                   required=False, default=""),
            Option("output",  "-o",       "Output file",
                   required=False, default="dalfox_out.txt"),
            Option("worker",  "--worker", "Number of workers",
                   type=OptionType.INTEGER, required=False, default=100),
            Option("headers", "--header", "Custom header (Header: Value)",
                   required=False, default=""),
            Option("cookie",  "--cookie", "Cookie string",
                   required=False, default=""),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        mode = opts.get("mode", "url")
        cmd = ["dalfox", mode, opts["url"]]
        if opts.get("blind"):
            cmd += ["--blind", opts["blind"]]
        if opts.get("output"):
            cmd += ["-o", opts["output"]]
        if opts.get("worker"):
            cmd += ["--worker", str(opts["worker"])]
        if opts.get("headers"):
            cmd += ["--header", opts["headers"]]
        if opts.get("cookie"):
            cmd += ["--cookie", opts["cookie"]]
        async for line in self._exec(cmd):
            yield line
