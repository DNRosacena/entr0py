"""entr0py.modules.passwords.crunch — Pattern-based wordlist generator."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Crunch(Module):
    meta = ModuleMeta(
        name="Crunch",
        slug="crunch",
        description=(
            "Generate wordlists from a character set with min/max length and patterns. "
            "Useful when you know partial password structure."
        ),
        category=Category.PASSWORDS,
        author="bofh28",
        version="3.6+",
        tags=["wordlist", "generator", "pattern", "brute-force"],
        tools=["crunch"],
    )

    def options(self) -> list[Option]:
        return [
            Option("min",     "",    "Minimum password length",
                   type=OptionType.INTEGER),
            Option("max",     "",    "Maximum password length",
                   type=OptionType.INTEGER),
            Option("charset", "",    "Character set (e.g. 'abcdefghijklmnopqrstuvwxyz')",
                   required=False, default="abcdefghijklmnopqrstuvwxyz0123456789"),
            Option("output",  "-o",  "Output file", required=False, default="crunch_out.txt"),
            Option("pattern", "-t",  "Pattern (@ for lowercase, , for uppercase, % for digits)",
                   required=False, default=""),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = ["crunch", str(opts["min"]), str(opts["max"]), opts.get("charset", "")]
        if opts.get("pattern"):
            cmd += ["-t", opts["pattern"]]
        if opts.get("output"):
            cmd += ["-o", opts["output"]]
        async for line in self._exec(cmd):
            yield line
