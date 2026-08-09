"""entr0py.modules.network.masscan — Internet-speed port scanning (>1M pkts/sec)."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Masscan(Module):
    meta = ModuleMeta(
        name="Masscan",
        slug="masscan",
        description=(
            "Blazing-fast TCP port scanner capable of scanning the entire Internet "
            "in under 6 minutes. Use for initial discovery, then follow up with nmap."
        ),
        category=Category.NETWORK,
        author="Robert Graham",
        version="1.3+",
        tags=["port-scan", "fast", "tcp", "network"],
        tools=["masscan"],
    )

    def options(self) -> list[Option]:
        return [
            Option("target",  "",          "Target IP range or CIDR"),
            Option("ports",   "-p",        "Port range (e.g. 0-65535 or 80,443,8080)",
                   required=False, default="0-65535"),
            Option("rate",    "--rate",    "Packets per second",
                   type=OptionType.INTEGER, required=False, default=10000),
            Option("output",  "-oL",       "Output file (list format)",
                   required=False, default="masscan_out.txt"),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = [
            "masscan", opts["target"],
            "-p", opts.get("ports", "0-65535"),
            "--rate", str(opts.get("rate", 10000)),
        ]
        if opts.get("output"):
            cmd += ["-oL", opts["output"]]
        async for line in self._exec(cmd):
            yield line
