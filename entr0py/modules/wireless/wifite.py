"""entr0py.modules.wireless.wifite — Automated WiFi attack tool."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Wifite(Module):
    meta = ModuleMeta(
        name="Wifite2",
        slug="wifite",
        description=(
            "Automated wireless auditing tool: WPA/WPA2 handshake capture, PMKID attack, "
            "WEP cracking, WPS pin attack, and PMKID cracking."
        ),
        category=Category.WIRELESS,
        author="derv82",
        version="2.x",
        tags=["wifi", "wpa", "wpa2", "handshake", "wps", "wireless"],
        tools=["wifite"],
    )

    def options(self) -> list[Option]:
        from entr0py.core.wordlists import default_path
        return [
            Option("interface", "--interface", "Wireless interface (e.g. wlan0)",
                   required=False, default=""),
            Option("kill",      "--kill",      "Kill interfering processes",
                   type=OptionType.BOOLEAN, required=False, default=True),
            Option("wpa",       "--wpa",       "Only target WPA networks",
                   type=OptionType.BOOLEAN, required=False, default=False),
            Option("pmkid",     "--pmkid",     "Use PMKID attack (no deauth needed)",
                   type=OptionType.BOOLEAN, required=False, default=False),
            Option("wordlist",  "--dict",      "Wordlist for cracking captured handshakes",
                   required=False, default=default_path("wifi")),
            Option("infinite",  "--infinite",  "Keep scanning after capturing",
                   type=OptionType.BOOLEAN, required=False, default=False),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = ["wifite"]
        if opts.get("interface"):
            cmd += ["--interface", opts["interface"]]
        if opts.get("kill", True):
            cmd.append("--kill")
        if opts.get("wpa"):
            cmd.append("--wpa")
        if opts.get("pmkid"):
            cmd.append("--pmkid")
        if opts.get("wordlist"):
            cmd += ["--dict", opts["wordlist"]]
        if opts.get("infinite"):
            cmd.append("--infinite")
        async for line in self._exec(cmd):
            yield line
