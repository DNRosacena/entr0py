"""entr0py.modules.network.nmap — The gold-standard port scanner."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Nmap(Module):
    meta = ModuleMeta(
        name="Nmap",
        slug="nmap",
        description=(
            "Network Mapper: port scanning, service/version detection, OS fingerprinting, "
            "and NSE scripting engine for 600+ scripts."
        ),
        category=Category.NETWORK,
        author="Gordon Lyon (Fyodor)",
        version="7.x",
        tags=["port-scan", "service-detect", "os-detect", "nse", "network"],
        tools=["nmap"],
    )

    def options(self) -> list[Option]:
        return [
            Option("target",    "",      "Target IP, range, or hostname"),
            Option("ports",     "-p",    "Port range (e.g. 1-1000, -, 22,80,443)",
                   required=False, default="-"),
            Option("scan_type", "",      "Scan type: sS (SYN), sV (version), sC (scripts), A (aggressive)",
                   type=OptionType.CHOICE,
                   choices=["sS", "sV", "sC", "A", "sU", "sn"],
                   required=False, default="sV"),
            Option("timing",    "-T",    "Timing template (0-5, 4=aggressive)",
                   type=OptionType.INTEGER, required=False, default=4),
            Option("output",    "-oN",   "Output file (normal format)",
                   required=False, default="nmap_out.txt"),
            Option("scripts",   "--script", "NSE script(s) to run (e.g. vuln, default, discovery)",
                   required=False, default=""),
            Option("os_detect", "-O",    "Enable OS detection (requires root)",
                   type=OptionType.BOOLEAN, required=False, default=False),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        scan_flag = f"-{opts.get('scan_type', 'sV')}"
        cmd = ["nmap", scan_flag, opts["target"]]
        cmd += ["-p", opts.get("ports", "-")]
        cmd += [f"-T{opts.get('timing', 4)}"]
        if opts.get("output"):
            cmd += ["-oN", opts["output"]]
        if opts.get("scripts"):
            cmd += ["--script", opts["scripts"]]
        if opts.get("os_detect"):
            cmd.append("-O")
        async for line in self._exec(cmd):
            yield line
