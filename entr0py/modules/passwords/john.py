"""entr0py.modules.passwords.john — John the Ripper CPU password cracker."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class John(Module):
    meta = ModuleMeta(
        name="John the Ripper",
        slug="john",
        description=(
            "Classic CPU-based password cracker with auto-detection of 100+ hash types. "
            "Excellent for /etc/shadow, ZIP, PDF, Office, and SSH key cracking."
        ),
        category=Category.PASSWORDS,
        author="Openwall",
        version="1.9+",
        tags=["hash-crack", "cpu", "offline", "shadow", "zip"],
        tools=["john"],
    )

    def options(self) -> list[Option]:
        from entr0py.core.wordlists import default_path
        return [
            Option("hashfile",  "",          "File containing hash(es)"),
            Option("wordlist",  "--wordlist", "Wordlist file",
                   required=False, default=default_path("passwords")),
            Option("format",    "--format",  "Hash format (auto-detected if omitted)",
                   required=False, default=""),
            Option("rules",     "--rules",   "Enable mangling rules",
                   type=OptionType.BOOLEAN, required=False, default=False),
            Option("show",      "--show",    "Show cracked passwords",
                   type=OptionType.BOOLEAN, required=False, default=False),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = ["john"]
        if opts.get("wordlist"):
            cmd.append(f"--wordlist={opts['wordlist']}")
        if opts.get("format"):
            cmd.append(f"--format={opts['format']}")
        if opts.get("rules"):
            cmd.append("--rules")
        if opts.get("show"):
            cmd.append("--show")
        cmd.append(opts["hashfile"])
        async for line in self._exec(cmd):
            yield line
