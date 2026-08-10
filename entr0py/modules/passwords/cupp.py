"""entr0py.modules.passwords.cupp — Custom User Password Profiling."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Cupp(Module):
    meta = ModuleMeta(
        name="CUPP",
        slug="cupp",
        description=(
            "Generate highly targeted wordlists based on target personal information "
            "(name, birthdate, pets, partner, etc) for tailored brute-force attacks."
        ),
        category=Category.PASSWORDS,
        author="Mebus",
        version="3.x",
        tags=["wordlist", "profiling", "targeted", "social-engineering"],
        repos={"cupp": "https://github.com/Mebus/cupp"},
    )

    def options(self) -> list[Option]:
        return [
            Option("interactive", "-i", "Run interactive profiling mode",
                   type=OptionType.BOOLEAN, required=False, default=True),
            Option("download",    "-l", "Download common wordlists from repository",
                   type=OptionType.BOOLEAN, required=False, default=False),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        import sys
        from entr0py.core.paths import TOOLS_DIR
        cupp_path = TOOLS_DIR / "cupp" / "cupp.py"
        if not cupp_path.exists():
            yield "[!] CUPP not found. Run: entr0py install cupp"
            return
        cmd = [sys.executable, str(cupp_path)]
        if opts.get("interactive", True):
            cmd.append("-i")
        elif opts.get("download"):
            cmd.append("-l")
        async for line in self._exec(cmd):
            yield line
