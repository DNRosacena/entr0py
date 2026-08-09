"""entr0py.modules.social.evilginx2 — Advanced man-in-the-middle phishing framework."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Evilginx2(Module):
    meta = ModuleMeta(
        name="Evilginx2",
        slug="evilginx2",
        description=(
            "Man-in-the-middle attack framework for capturing credentials and session "
            "cookies, bypassing 2FA. Uses 'phishlets' to proxy real websites."
        ),
        category=Category.SOCIAL,
        author="kgretzky",
        version="3.x",
        tags=["phishing", "mitm", "2fa-bypass", "session-hijack", "credentials"],
        tools=["evilginx2"],
    )

    def options(self) -> list[Option]:
        return [
            Option("phishlets_path", "-p",  "Path to phishlets directory",
                   required=False, default=""),
            Option("developer",      "-developer", "Run in developer mode (no real DNS)",
                   type=OptionType.BOOLEAN, required=False, default=False),
            Option("debug",          "-debug", "Enable debug logging",
                   type=OptionType.BOOLEAN, required=False, default=False),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = ["evilginx2"]
        if opts.get("phishlets_path"):
            cmd += ["-p", opts["phishlets_path"]]
        if opts.get("developer"):
            cmd.append("-developer")
        if opts.get("debug"):
            cmd.append("-debug")
        yield "[*] Starting Evilginx2 — configure phishlets and lures via the interactive shell."
        async for line in self._exec(cmd):
            yield line
