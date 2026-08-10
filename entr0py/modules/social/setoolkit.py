"""entr0py.modules.social.setoolkit — Social Engineering Toolkit."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option


class Setoolkit(Module):
    meta = ModuleMeta(
        name="Social-Engineer Toolkit",
        slug="setoolkit",
        description=(
            "The premier social engineering framework: phishing, credential harvesting, "
            "malicious payload generation, and mass email attacks."
        ),
        category=Category.SOCIAL,
        author="TrustedSec",
        version="8.x",
        tags=["social-engineering", "phishing", "harvesting", "payload"],
        # Kali's `set` apt package provides the `setoolkit` binary; `set` alone is a
        # shell builtin (never resolvable via shutil.which) and run() only calls setoolkit.
        tools=["setoolkit"],
    )

    def options(self) -> list[Option]:
        return [
            Option("command",  "",   "Non-interactive command string (for automation)",
                   required=False, default=""),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        import platform
        if platform.system().lower().startswith("win"):
            yield "[!] Social-Engineer Toolkit is Linux/macOS only — not supported on Windows."
            return
        if opts.get("command"):
            async for line in self._exec_shell(
                f'echo "{opts["command"]}" | setoolkit'
            ):
                yield line
        else:
            yield "[*] Launching SET in interactive mode…"
            async for line in self._exec(["setoolkit"]):
                yield line
