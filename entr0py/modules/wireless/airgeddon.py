"""entr0py.modules.wireless.airgeddon — Wireless auditing framework (launcher)."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option
from entr0py.core.paths import TOOLS_DIR


class Airgeddon(Module):
    meta = ModuleMeta(
        name="airgeddon",
        slug="airgeddon",
        description=(
            "Multi-use wireless auditing framework: handshake/PMKID capture, WPA/WPA2 "
            "cracking, evil-twin/rogue AP, WPS and deauth attacks. Interactive menu."
        ),
        category=Category.WIRELESS,
        author="v1s1t0r1sh3r3",
        version="11.x",
        tags=["wireless", "wifi", "wpa", "evil-twin", "handshake", "framework"],
        repos={"airgeddon": "https://github.com/v1s1t0r1sh3r3/airgeddon"},
        tools=[],   # the airgeddon.sh script (git-cloned into TOOLS_DIR) is the tool
        offensive=True,
    )

    def options(self) -> list[Option]:
        return []   # airgeddon is a fully interactive menu — no headless options

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        script = TOOLS_DIR / "airgeddon" / "airgeddon.sh"
        if not script.exists():
            yield f"[!] airgeddon not found at {script}. Run: entr0py install airgeddon"
            return
        yield "[*] Launching airgeddon — interactive; needs root + a monitor-mode Wi-Fi adapter."
        yield "    In Docker: run with --privileged and pass through your wireless interface."
        async for line in self._exec(["bash", str(script)]):
            yield line
