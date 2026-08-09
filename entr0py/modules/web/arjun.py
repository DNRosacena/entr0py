"""entr0py.modules.web.arjun — HTTP parameter discovery suite."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Arjun(Module):
    meta = ModuleMeta(
        name="Arjun",
        slug="arjun",
        description=(
            "HTTP parameter discovery: find hidden GET/POST/JSON/XML parameters "
            "on web endpoints by comparing response differences."
        ),
        category=Category.WEB,
        author="s0md3v",
        version="2.x",
        tags=["parameter", "hidden-params", "get", "post", "discovery"],
        packages=["arjun"],
        tools=["arjun"],
    )

    def options(self) -> list[Option]:
        return [
            Option("url",     "-u",   "Target URL"),
            Option("method",  "-m",   "HTTP method (GET|POST|JSON|XML)",
                   type=OptionType.CHOICE,
                   choices=["GET", "POST", "JSON", "XML"],
                   required=False, default="GET"),
            Option("output",  "-o",   "Output file (JSON)",
                   required=False, default="arjun_out.json"),
            Option("wordlist", "-w",  "Custom parameter wordlist",
                   required=False, default=""),
            Option("threads",  "-t",  "Threads",
                   type=OptionType.INTEGER, required=False, default=5),
            Option("delay",    "--delay", "Delay between requests (seconds)",
                   type=OptionType.INTEGER, required=False, default=0),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = ["arjun", "-u", opts["url"], "-m", opts.get("method", "GET")]
        if opts.get("output"):
            cmd += ["-o", opts["output"]]
        if opts.get("wordlist"):
            cmd += ["-w", opts["wordlist"]]
        if opts.get("threads"):
            cmd += ["-t", str(opts["threads"])]
        if opts.get("delay"):
            cmd += ["--delay", str(opts["delay"])]
        async for line in self._exec(cmd):
            yield line
