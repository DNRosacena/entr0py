"""entr0py.modules.osint.holehe — Email-to-account mapping across 120+ services."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Holehe(Module):
    meta = ModuleMeta(
        name="Holehe",
        slug="holehe",
        description=(
            "Check if an email address is registered on 120+ websites "
            "(Twitter, Instagram, GitHub, Adobe, etc) without triggering alerts."
        ),
        category=Category.OSINT,
        author="megadose",
        version="1.x",
        tags=["email", "osint", "accounts"],
        packages=["holehe"],
        tools=["holehe"],
        offensive=False,
    )

    def options(self) -> list[Option]:
        return [
            Option("email",  "",        "Target email address"),
            Option("only_used", "--only-used", "Only show sites where email is registered",
                   type=OptionType.BOOLEAN, required=False, default=True),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = ["holehe", opts["email"]]
        if opts.get("only_used"):
            cmd.append("--only-used")
        async for line in self._exec(cmd):
            yield line
