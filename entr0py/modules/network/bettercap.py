"""entr0py.modules.network.bettercap — Swiss-army knife for network attacks."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Bettercap(Module):
    meta = ModuleMeta(
        name="Bettercap",
        slug="bettercap",
        description=(
            "Full-featured network attack and monitoring framework: ARP spoofing, "
            "MITM, WiFi attacks, BLE scanning, HID injection, and HTTP/S proxying."
        ),
        category=Category.NETWORK,
        author="evilsocket",
        version="2.x",
        tags=["mitm", "arp", "wifi", "proxy", "network-attack"],
        tools=["bettercap"],
    )

    def options(self) -> list[Option]:
        return [
            Option("iface",    "-iface",  "Network interface (e.g. eth0, wlan0)"),
            Option("caplet",   "-caplet", "Caplet script to run automatically",
                   required=False, default=""),
            Option("eval",     "-eval",   "Commands to evaluate on start",
                   required=False, default=""),
            Option("no_colors", "-no-colors", "Disable colored output",
                   type=OptionType.BOOLEAN, required=False, default=False),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = ["bettercap", "-iface", opts["iface"]]
        if opts.get("caplet"):
            cmd += ["-caplet", opts["caplet"]]
        if opts.get("eval"):
            cmd += ["-eval", opts["eval"]]
        if opts.get("no_colors"):
            cmd.append("-no-colors")
        async for line in self._exec(cmd):
            yield line
