"""entr0py.modules.recon.subfinder — Passive subdomain enumeration.

Replaces: Sublist3r (broken/stale sources)
Why better: actively maintained by ProjectDiscovery, 40+ passive sources,
            supports config file for API keys, outputs JSON/CSV.
"""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Subfinder(Module):
    meta = ModuleMeta(
        name="Subfinder",
        slug="subfinder",
        description=(
            "Fast passive subdomain enumeration using 40+ online sources "
            "(VirusTotal, Shodan, CertSpotter, etc). Replaces Sublist3r."
        ),
        category=Category.RECON,
        author="ProjectDiscovery",
        version="2.x",
        tags=["subdomain", "passive", "recon", "dns"],
        tools=["subfinder"],
        replaces=["Sublist3r"],
    )

    def options(self) -> list[Option]:
        return [
            Option("domain",  "-d",   "Target domain (e.g. example.com)"),
            Option("output",  "-o",   "Output file path",
                   required=False, default="subfinder_out.txt"),
            Option("threads", "-t",   "Concurrency level",
                   type=OptionType.INTEGER, required=False, default=10),
            Option("all",     "-all", "Use all sources (slower but thorough)",
                   type=OptionType.BOOLEAN, required=False, default=False),
            Option("json",    "-oJ",  "Output as JSON",
                   type=OptionType.BOOLEAN, required=False, default=False),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = ["subfinder", "-d", opts["domain"], "-silent"]
        if opts.get("output"):
            cmd += ["-o", opts["output"]]
        if opts.get("threads"):
            cmd += ["-t", str(opts["threads"])]
        if opts.get("all"):
            cmd.append("-all")
        if opts.get("json"):
            cmd.append("-oJ")
        async for line in self._exec(cmd):
            yield line

    def parse(self, lines: list[str]) -> list[str]:
        """`-silent` prints one bare hostname per line."""
        out = []
        for raw in lines:
            s = raw.strip()
            if s and " " not in s and "." in s and not s.startswith(("[", "-")):
                out.append(s)
        return sorted(set(out))
