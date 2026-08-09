"""entr0py.modules.recon.katana — Fast web crawler and content discovery.

Replaces: Photon (unmaintained, slow, broken JS parsing)
Why better: ProjectDiscovery, headless JS rendering, scope-aware, structured output.
"""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Katana(Module):
    meta = ModuleMeta(
        name="Katana",
        slug="katana",
        description=(
            "Next-gen web crawler with headless JS rendering support. "
            "Discovers endpoints, forms, JS files, and hidden parameters."
        ),
        category=Category.RECON,
        author="ProjectDiscovery",
        version="1.x",
        tags=["crawler", "web", "endpoints", "js", "discovery"],
        tools=["katana"],
        replaces=["Photon"],
    )

    def options(self) -> list[Option]:
        return [
            Option("target",   "-u",   "Target URL"),
            Option("depth",    "-d",   "Crawl depth",
                   type=OptionType.INTEGER, required=False, default=3),
            Option("headless", "-hl",  "Use headless browser (JS rendering)",
                   type=OptionType.BOOLEAN, required=False, default=False),
            Option("js_crawl", "-jc",  "Parse JS files for endpoints",
                   type=OptionType.BOOLEAN, required=False, default=True),
            Option("output",   "-o",   "Output file", required=False, default="katana_out.txt"),
            Option("concurrency", "-c", "Concurrency",
                   type=OptionType.INTEGER, required=False, default=10),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = ["katana", "-u", opts["target"], "-silent"]
        cmd += ["-d", str(opts.get("depth", 3))]
        cmd += ["-c", str(opts.get("concurrency", 10))]
        if opts.get("headless"):
            cmd.append("-hl")
        if opts.get("js_crawl"):
            cmd.append("-jc")
        if opts.get("output"):
            cmd += ["-o", opts["output"]]
        async for line in self._exec(cmd):
            yield line
