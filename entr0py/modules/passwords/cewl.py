"""entr0py.modules.passwords.cewl — Website-based custom wordlist generator."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Cewl(Module):
    meta = ModuleMeta(
        name="CeWL",
        slug="cewl",
        description=(
            "Spider a target website and generate a custom wordlist from the content. "
            "Ideal for targeted password attacks where generic lists fail."
        ),
        category=Category.PASSWORDS,
        author="digininja",
        version="6.x",
        tags=["wordlist", "spider", "custom", "web"],
        tools=["cewl"],
    )

    def options(self) -> list[Option]:
        return [
            Option("url",    "",    "Target URL to spider"),
            Option("depth",  "-d",  "Spider depth",
                   type=OptionType.INTEGER, required=False, default=2),
            Option("min",    "-m",  "Minimum word length",
                   type=OptionType.INTEGER, required=False, default=5),
            Option("output", "-w",  "Output wordlist file",
                   required=False, default="cewl_wordlist.txt"),
            Option("with_numbers", "--with-numbers",
                   "Accept words with numbers",
                   type=OptionType.BOOLEAN, required=False, default=False),
            Option("email", "-e", "Include emails in output",
                   type=OptionType.BOOLEAN, required=False, default=False),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = [
            "cewl", opts["url"],
            "-d", str(opts.get("depth", 2)),
            "-m", str(opts.get("min", 5)),
        ]
        if opts.get("output"):
            cmd += ["-w", opts["output"]]
        if opts.get("with_numbers"):
            cmd.append("--with-numbers")
        if opts.get("email"):
            cmd.append("-e")
        async for line in self._exec(cmd):
            yield line
