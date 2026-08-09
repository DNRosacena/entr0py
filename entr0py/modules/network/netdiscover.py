"""entr0py.modules.network.netdiscover — ARP-based network host discovery."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Netdiscover(Module):
    meta = ModuleMeta(
        name="Netdiscover",
        slug="netdiscover",
        description=(
            "Active/passive ARP reconnaissance for local network discovery. "
            "Identifies live hosts, MAC addresses, and vendors without port scanning."
        ),
        category=Category.NETWORK,
        author="Jaime Penalba",
        version="0.10+",
        tags=["arp", "host-discovery", "lan", "passive"],
        tools=["netdiscover"],
    )

    def options(self) -> list[Option]:
        return [
            Option("range",   "-r",  "IP range (e.g. 192.168.1.0/24)",
                   required=False, default=""),
            Option("iface",   "-i",  "Network interface",
                   required=False, default=""),
            Option("passive", "-p",  "Passive mode (listen only, no ARP requests)",
                   type=OptionType.BOOLEAN, required=False, default=False),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = ["netdiscover"]
        if opts.get("range"):
            cmd += ["-r", opts["range"]]
        if opts.get("iface"):
            cmd += ["-i", opts["iface"]]
        if opts.get("passive"):
            cmd.append("-p")
        async for line in self._exec(cmd):
            yield line
