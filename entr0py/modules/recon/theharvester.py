"""entr0py.modules.recon.theharvester — Email, host, and employee recon."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class TheHarvester(Module):
    meta = ModuleMeta(
        name="theHarvester",
        slug="theharvester",
        description=(
            "Gather emails, names, subdomains, IPs, and URLs from public sources "
            "(Google, Bing, LinkedIn, Shodan, VirusTotal, etc)."
        ),
        category=Category.RECON,
        author="laramies",
        version="4.x",
        tags=["email", "osint", "subdomain", "passive"],
        packages=["theHarvester"],
        tools=["theHarvester"],
    )

    def options(self) -> list[Option]:
        return [
            Option("domain",  "-d", "Target domain"),
            Option("source",  "-b", "Data source (google, bing, linkedin, all, …)",
                   required=False, default="all"),
            Option("limit",   "-l", "Limit number of results",
                   type=OptionType.INTEGER, required=False, default=500),
            Option("output",  "-f", "Output filename (HTML + XML)",
                   required=False, default="harvester_out"),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = [
            "theHarvester",
            "-d", opts["domain"],
            "-b", opts.get("source", "all"),
            "-l", str(opts.get("limit", 500)),
        ]
        if opts.get("output"):
            cmd += ["-f", opts["output"]]
        async for line in self._exec(cmd):
            yield line
