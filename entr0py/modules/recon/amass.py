"""entr0py.modules.recon.amass — Comprehensive attack surface mapping.

OWASP Amass performs deep DNS enumeration, graph-based asset discovery,
and external API integration.  Use alongside subfinder for thorough coverage.
"""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Amass(Module):
    meta = ModuleMeta(
        name="Amass",
        slug="amass",
        description=(
            "OWASP attack-surface mapping: DNS enum, scraping, cert transparency, "
            "and graph-based asset discovery across 50+ data sources."
        ),
        category=Category.RECON,
        author="OWASP",
        version="4.x",
        tags=["subdomain", "dns", "active", "passive", "graph", "owasp"],
        tools=["amass"],
    )

    def options(self) -> list[Option]:
        from entr0py.core.wordlists import default_path
        return [
            Option("domain",  "-d",       "Target domain"),
            Option("output",  "-o",       "Output file", required=False, default="amass_out.txt"),
            Option("passive", "-passive", "Passive mode only (no brute-force)",
                   type=OptionType.BOOLEAN, required=False, default=True),
            Option("brute",   "-brute",   "Enable brute-force subdomain discovery",
                   type=OptionType.BOOLEAN, required=False, default=False),
            Option("wordlist", "-w",      "Wordlist for brute-force",
                   required=False, default=default_path("dns")),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = ["amass", "enum", "-d", opts["domain"]]
        if opts.get("passive"):
            cmd.append("-passive")
        if opts.get("brute"):
            cmd.append("-brute")
            if opts.get("wordlist"):
                cmd += ["-w", opts["wordlist"]]
        if opts.get("output"):
            cmd += ["-o", opts["output"]]
        async for line in self._exec(cmd):
            yield line
