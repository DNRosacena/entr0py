"""entr0py.modules.wireless.hcxdumptool — WPA PMKID and handshake capture tool."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Hcxdumptool(Module):
    meta = ModuleMeta(
        name="hcxdumptool",
        slug="hcxdumptool",
        description=(
            "Capture WPA PMKID and EAPOL handshakes in pcapng format. "
            "Used with hcxtools to convert for hashcat cracking without deauth."
        ),
        category=Category.WIRELESS,
        author="ZerBea",
        version="6.x",
        tags=["wifi", "pmkid", "capture", "wpa3", "eapol"],
        tools=["hcxdumptool", "hcxpcapngtool"],
    )

    def options(self) -> list[Option]:
        return [
            Option("interface", "-i",  "Wireless interface (must support monitor mode)"),
            Option("output",    "-o",  "Output pcapng file",
                   required=False, default="capture.pcapng"),
            Option("filterlist", "--filterlist_ap",
                   "BSSID whitelist file (one MAC per line)",
                   required=False, default=""),
            Option("duration",   "",   "Capture duration in seconds (0=unlimited)",
                   type=OptionType.INTEGER, required=False, default=60),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = ["hcxdumptool", "-i", opts["interface"], "-o", opts.get("output", "capture.pcapng")]
        if opts.get("filterlist"):
            cmd += ["--filterlist_ap", opts["filterlist"]]
        duration = opts.get("duration", 60)
        if duration:
            cmd += ["--tot", str(duration)]
        async for line in self._exec(cmd):
            yield line
