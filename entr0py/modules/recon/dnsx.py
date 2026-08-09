"""entr0py.modules.recon.dnsx — DNS resolution and brute-force toolkit."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Dnsx(Module):
    meta = ModuleMeta(
        name="dnsx",
        slug="dnsx",
        description=(
            "Fast, multi-purpose DNS toolkit: bulk resolution, wildcard filtering, "
            "DNS brute-force, CNAME/A/MX record extraction."
        ),
        category=Category.RECON,
        author="ProjectDiscovery",
        version="1.x",
        tags=["dns", "brute-force", "resolution", "subdomain"],
        tools=["dnsx"],
    )

    def options(self) -> list[Option]:
        from entr0py.core.wordlists import default_path
        return [
            Option("input",    "-l",    "File with list of domains/subdomains to resolve"),
            Option("wordlist", "-w",    "Wordlist for DNS brute-force",
                   required=False, default=default_path("dns")),
            Option("domain",   "-d",    "Target domain for brute-force",
                   required=False, default=""),
            Option("threads",  "-t",    "Concurrency",
                   type=OptionType.INTEGER, required=False, default=100),
            Option("output",   "-o",    "Output file", required=False, default="dnsx_out.txt"),
            Option("resp",     "-resp", "Show DNS response",
                   type=OptionType.BOOLEAN, required=False, default=True),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = ["dnsx", "-t", str(opts.get("threads", 100)), "-silent"]
        if opts.get("input"):
            cmd += ["-l", opts["input"]]
        if opts.get("wordlist") and opts.get("domain"):
            cmd += ["-w", opts["wordlist"], "-d", opts["domain"]]
        if opts.get("output"):
            cmd += ["-o", opts["output"]]
        if opts.get("resp"):
            cmd.append("-resp")
        async for line in self._exec(cmd):
            yield line
