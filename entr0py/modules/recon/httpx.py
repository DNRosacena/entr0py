"""entr0py.modules.recon.httpx — Fast HTTP probing and fingerprinting.

Replaces: HydraRecon (unmaintained)
Why better: actively maintained by ProjectDiscovery, supports bulk probing,
            tech detection, status codes, title extraction, screenshots.
"""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Httpx(Module):
    meta = ModuleMeta(
        name="httpx",
        slug="httpx",
        description=(
            "Multi-purpose HTTP toolkit: bulk probe hosts for live HTTP/S services, "
            "extract titles, tech stack, status codes, and CDN info."
        ),
        category=Category.RECON,
        author="ProjectDiscovery",
        version="1.x",
        tags=["http", "probe", "fingerprint", "tech-detect"],
        tools=["httpx"],
        replaces=["HydraRecon"],
    )

    def options(self) -> list[Option]:
        return [
            Option("input",    "-l",   "File with list of hosts/URLs"),
            Option("target",   "-u",   "Single target URL/host",
                   required=False, default=""),
            Option("threads",  "-t",   "Concurrency",
                   type=OptionType.INTEGER, required=False, default=50),
            Option("output",   "-o",   "Output file", required=False, default="httpx_out.txt"),
            Option("tech",     "-td",  "Enable technology detection",
                   type=OptionType.BOOLEAN, required=False, default=True),
            Option("title",    "-title", "Extract page titles",
                   type=OptionType.BOOLEAN, required=False, default=True),
            Option("status",   "-sc",  "Show status codes",
                   type=OptionType.BOOLEAN, required=False, default=True),
            Option("silent",   "-silent", "Silent mode",
                   type=OptionType.BOOLEAN, required=False, default=False),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = ["httpx"]
        if opts.get("input"):
            cmd += ["-l", opts["input"]]
        elif opts.get("target"):
            cmd += ["-u", opts["target"]]
        else:
            yield "[!] Provide either 'input' (file) or 'target' (single host)."
            return
        cmd += ["-t", str(opts.get("threads", 50))]
        if opts.get("output"):
            cmd += ["-o", opts["output"]]
        if opts.get("tech"):
            cmd.append("-td")
        if opts.get("title"):
            cmd.append("-title")
        if opts.get("status"):
            cmd.append("-sc")
        if opts.get("silent"):
            cmd.append("-silent")
        async for line in self._exec(cmd):
            yield line
