"""entr0py.modules.wireless.aircrack — Aircrack-ng suite for wireless auditing."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Aircrack(Module):
    meta = ModuleMeta(
        name="Aircrack-ng",
        slug="aircrack",
        description=(
            "The de-facto standard wireless auditing suite: airmon-ng (monitor mode), "
            "airodump-ng (capture), aireplay-ng (injection), aircrack-ng (cracking)."
        ),
        category=Category.WIRELESS,
        author="Thomas d'Otreppe",
        version="1.7+",
        tags=["wifi", "wpa", "wep", "capture", "crack", "monitor"],
        tools=["aircrack-ng", "airodump-ng", "aireplay-ng", "airmon-ng"],
    )

    def options(self) -> list[Option]:
        from entr0py.core.wordlists import default_path
        return [
            Option("mode",      "",      "Mode: monitor | capture | crack",
                   type=OptionType.CHOICE,
                   choices=["monitor", "capture", "crack"],
                   required=False, default="crack"),
            Option("interface", "",      "Wireless interface",
                   required=False, default="wlan0"),
            Option("capfile",   "",      "Capture file (.cap) for cracking",
                   required=False, default=""),
            Option("wordlist",  "-w",    "Wordlist for cracking",
                   required=False, default=default_path("wifi")),
            Option("bssid",     "--bssid", "Target BSSID",
                   required=False, default=""),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        mode = opts.get("mode", "crack")
        if mode == "monitor":
            async for line in self._exec(["airmon-ng", "start", opts.get("interface", "wlan0")]):
                yield line
        elif mode == "capture":
            cmd = ["airodump-ng", opts.get("interface", "wlan0mon")]
            if opts.get("bssid"):
                cmd += ["--bssid", opts["bssid"]]
            async for line in self._exec(cmd):
                yield line
        else:  # crack
            if not opts.get("capfile") or not opts.get("wordlist"):
                yield "[!] 'capfile' and 'wordlist' are required for crack mode."
                return
            cmd = ["aircrack-ng", "-w", opts["wordlist"], opts["capfile"]]
            if opts.get("bssid"):
                cmd += ["--bssid", opts["bssid"]]
            async for line in self._exec(cmd):
                yield line
