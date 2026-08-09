"""entr0py.modules.network.rustscan — Insanely fast Rust-based port scanner."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class RustScan(Module):
    meta = ModuleMeta(
        name="RustScan",
        slug="rustscan",
        description=(
            "Rust-powered port scanner: scans all 65k ports in ~3 seconds, "
            "then auto-pipes results to nmap for service/version detection."
        ),
        category=Category.NETWORK,
        author="brandonskerritt",
        version="2.x",
        tags=["port-scan", "fast", "rust", "nmap-integration"],
        tools=["rustscan"],
    )

    def options(self) -> list[Option]:
        return [
            Option("target",   "-a",   "Target IP or hostname"),
            Option("ports",    "-p",   "Specific ports (default: all 65535)",
                   required=False, default=""),
            Option("batch",    "-b",   "Batch size (sockets open at once)",
                   type=OptionType.INTEGER, required=False, default=4500),
            Option("timeout",  "-t",   "Timeout in milliseconds",
                   type=OptionType.INTEGER, required=False, default=1500),
            Option("nmap_args", "--",  "Arguments to pass to nmap after discovery",
                   required=False, default="-sV -sC"),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = [
            "rustscan",
            "-a", opts["target"],
            "-b", str(opts.get("batch", 4500)),
            "-t", str(opts.get("timeout", 1500)),
        ]
        if opts.get("ports"):
            cmd += ["-p", opts["ports"]]
        nmap_args = opts.get("nmap_args", "-sV -sC")
        if nmap_args:
            cmd += ["--", *nmap_args.split()]
        async for line in self._exec(cmd):
            yield line
