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
            Option("mode",      "", "monitor | capture | deauth | crack",
                   type=OptionType.CHOICE,
                   choices=["monitor", "capture", "deauth", "crack"],
                   required=False, default="crack"),
            Option("interface", "", "Wireless interface (wlan0, or wlan0mon once in monitor mode)",
                   required=False, default="wlan0"),
            Option("bssid",     "--bssid", "Target AP BSSID / MAC (capture filter, deauth, crack)",
                   required=False, default=""),
            # capture
            Option("channel",   "-c", "Lock to a channel [capture]",
                   required=False, default=""),
            Option("write",     "-w", "Write-file prefix — REQUIRED to save a .cap you can crack [capture]",
                   required=False, default=""),
            Option("band",      "--band", "Band(s): a | bg | abg [capture]",
                   required=False, default=""),
            # deauth
            Option("client",    "-c", "Client MAC to target; blank = broadcast [deauth]",
                   required=False, default=""),
            Option("count",     "", "Deauth packet count; 0 = continuous [deauth]",
                   type=OptionType.INTEGER, required=False, default=10),
            # monitor
            Option("check_kill", "", "Kill interfering processes (NetworkManager, …) first [monitor]",
                   type=OptionType.BOOLEAN, required=False, default=True),
            # crack
            Option("capfile",   "", "Capture .cap file to crack [crack]",
                   required=False, default=""),
            Option("wordlist",  "-w", "Wordlist for WPA cracking [crack]",
                   required=False, default=default_path("wifi")),
            Option("encryption", "", "Cipher: wpa | wep (WEP needs no wordlist) [crack]",
                   type=OptionType.CHOICE, choices=["wpa", "wep"],
                   required=False, default="wpa"),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        mode  = opts.get("mode", "crack")
        iface = opts.get("interface", "wlan0")

        if mode == "monitor":
            if opts.get("check_kill"):
                yield "[*] Killing interfering processes (airmon-ng check kill)…"
                async for line in self._exec(["airmon-ng", "check", "kill"]):
                    yield line
            async for line in self._exec(["airmon-ng", "start", iface]):
                yield line

        elif mode == "capture":
            cmd = ["airodump-ng"]
            if opts.get("bssid"):
                cmd += ["--bssid", opts["bssid"]]
            if opts.get("channel"):
                cmd += ["-c", str(opts["channel"])]
            if opts.get("band"):
                cmd += ["--band", opts["band"]]
            if opts.get("write"):
                cmd += ["-w", opts["write"]]
            else:
                yield "[*] Tip: set 'write' to save a .cap — without it nothing is captured to disk."
            cmd.append(iface)
            async for line in self._exec(cmd):
                yield line

        elif mode == "deauth":
            if not opts.get("bssid"):
                yield "[!] 'bssid' (target AP) is required for deauth mode."
                return
            count = str(opts.get("count", 10))
            cmd = ["aireplay-ng", "--deauth", count, "-a", opts["bssid"]]
            if opts.get("client"):
                cmd += ["-c", opts["client"]]
            cmd.append(iface)
            yield f"[*] Deauthing {count} pkt(s) at {opts['bssid']} — forces clients to re-handshake."
            async for line in self._exec(cmd):
                yield line

        else:  # crack
            if not opts.get("capfile"):
                yield "[!] 'capfile' is required for crack mode."
                return
            cmd = ["aircrack-ng"]
            if opts.get("bssid"):
                cmd += ["--bssid", opts["bssid"]]
            if opts.get("encryption", "wpa") == "wep":
                cmd.append("-a1")   # WEP — no wordlist needed
            else:
                if not opts.get("wordlist"):
                    yield "[!] 'wordlist' is required to crack WPA/WPA2."
                    return
                cmd += ["-w", opts["wordlist"]]
            cmd.append(opts["capfile"])
            async for line in self._exec(cmd):
                yield line
