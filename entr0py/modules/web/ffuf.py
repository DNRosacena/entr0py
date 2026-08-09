"""entr0py.modules.web.ffuf — Fast web fuzzer for directory/vhost/param discovery."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Ffuf(Module):
    meta = ModuleMeta(
        name="ffuf",
        slug="ffuf",
        description=(
            "Fuzz Faster U Fool: high-speed web fuzzer for directory brute-forcing, "
            "virtual host discovery, parameter fuzzing, and more."
        ),
        category=Category.WEB,
        author="ffuf",
        version="2.x",
        tags=["fuzzing", "directory", "brute-force", "vhost", "wordlist"],
        tools=["ffuf"],
    )

    def options(self) -> list[Option]:
        from entr0py.core.wordlists import default_path
        return [
            Option("url",      "-u",  "Target URL with FUZZ keyword (e.g. http://site.com/FUZZ)"),
            Option("wordlist", "-w",  "Wordlist path",
                   required=False, default=default_path("web")),
            Option("threads",  "-t",  "Threads",
                   type=OptionType.INTEGER, required=False, default=40),
            Option("filter_code", "-fc", "Filter HTTP status codes (e.g. 404,403)",
                   required=False, default="404"),
            Option("match_code",  "-mc", "Match HTTP status codes",
                   required=False, default=""),
            Option("extensions",  "-e",  "File extensions to fuzz (e.g. .php,.html,.bak)",
                   required=False, default=""),
            Option("output",   "-o",  "Output file", required=False, default="ffuf_out.json"),
            Option("output_fmt", "-of", "Output format (json|ejson|html|md|csv|ecsv)",
                   required=False, default="json"),
            Option("recursion", "-recursion", "Enable recursive fuzzing",
                   type=OptionType.BOOLEAN, required=False, default=False),
            Option("headers",  "-H",  "Custom headers (Header: Value)",
                   required=False, default=""),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = ["ffuf", "-u", opts["url"], "-w", opts["wordlist"]]
        cmd += ["-t", str(opts.get("threads", 40))]
        if opts.get("filter_code"):
            cmd += ["-fc", opts["filter_code"]]
        if opts.get("match_code"):
            cmd += ["-mc", opts["match_code"]]
        if opts.get("extensions"):
            cmd += ["-e", opts["extensions"]]
        if opts.get("output"):
            cmd += ["-o", opts["output"], "-of", opts.get("output_fmt", "json")]
        if opts.get("recursion"):
            cmd.append("-recursion")
        if opts.get("headers"):
            cmd += ["-H", opts["headers"]]
        async for line in self._exec(cmd):
            yield line
