"""entr0py.modules.passwords.hashcat — GPU-accelerated password recovery."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Hashcat(Module):
    meta = ModuleMeta(
        name="Hashcat",
        slug="hashcat",
        description=(
            "World's fastest GPU-based password cracker. Supports 350+ hash types "
            "and 5 attack modes: wordlist, combinator, brute-force, hybrid, PRINCE."
        ),
        category=Category.PASSWORDS,
        author="Jens Steube",
        version="6.x",
        tags=["hash-crack", "gpu", "offline", "wordlist", "brute-force"],
        tools=["hashcat"],
    )

    def options(self) -> list[Option]:
        from entr0py.core.wordlists import default_path
        return [
            Option("hashfile",   "",     "File containing hash(es) to crack"),
            Option("hash_type",  "-m",   "Hash type (0=MD5, 1000=NTLM, 1800=SHA512crypt, …)",
                   type=OptionType.INTEGER, required=False, default=0),
            Option("attack_mode","-a",   "Attack mode (0=wordlist, 3=brute-force, 6=hybrid)",
                   type=OptionType.INTEGER, required=False, default=0),
            Option("wordlist",   "",     "Wordlist file (attack mode 0/6)",
                   required=False, default=default_path("passwords")),
            Option("mask",       "",     "Mask for brute-force (e.g. ?a?a?a?a?a?a)",
                   required=False, default=""),
            Option("rules",      "-r",   "Rule file", required=False, default=""),
            Option("output",     "-o",   "Output file for cracked hashes",
                   required=False, default="hashcat_cracked.txt"),
            Option("show",       "--show","Show already-cracked hashes",
                   type=OptionType.BOOLEAN, required=False, default=False),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = [
            "hashcat",
            "-m", str(opts.get("hash_type", 0)),
            "-a", str(opts.get("attack_mode", 0)),
        ]
        if opts.get("output"):
            cmd += ["-o", opts["output"]]
        if opts.get("show"):
            cmd.append("--show")
        if opts.get("rules"):
            cmd += ["-r", opts["rules"]]
        cmd.append(opts["hashfile"])
        if opts.get("wordlist"):
            cmd.append(opts["wordlist"])
        elif opts.get("mask"):
            cmd.append(opts["mask"])
        async for line in self._exec(cmd):
            yield line
