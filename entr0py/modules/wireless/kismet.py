"""entr0py.modules.wireless.kismet — Passive wireless monitoring and IDS."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Kismet(Module):
    meta = ModuleMeta(
        name="Kismet",
        slug="kismet",
        description=(
            "Passive 802.11 / Bluetooth / ZigBee / SDR wireless monitoring, "
            "IDS, and wardriving tool with a web UI."
        ),
        category=Category.WIRELESS,
        author="kismetwireless",
        version="2022+",
        tags=["wifi", "bluetooth", "passive", "monitoring", "ids", "wardriving"],
        tools=["kismet"],
        offensive=False,
    )

    def options(self) -> list[Option]:
        return [
            Option("interface", "-c",   "Capture source (e.g. wlan0)"),
            Option("log_prefix","--log-prefix", "Log file prefix",
                   required=False, default="kismet_log"),
            Option("no_logging","--no-logging", "Disable logging",
                   type=OptionType.BOOLEAN, required=False, default=False),
            Option("daemonize", "--daemonize", "Run as daemon",
                   type=OptionType.BOOLEAN, required=False, default=False),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = ["kismet", "-c", opts["interface"]]
        cmd += ["--log-prefix", opts.get("log_prefix", "kismet_log")]
        if opts.get("no_logging"):
            cmd.append("--no-logging")
        if opts.get("daemonize"):
            cmd.append("--daemonize")
        async for line in self._exec(cmd):
            yield line
