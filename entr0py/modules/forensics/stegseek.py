"""entr0py.modules.forensics.stegseek — Lightning-fast steganography cracker."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Stegseek(Module):
    meta = ModuleMeta(
        name="Stegseek",
        slug="stegseek",
        description=(
            "Crack steghide-encrypted steganography 1000x faster than steghide itself. "
            "Can crack a 1.9GB rockyou wordlist in ~1.9 seconds."
        ),
        category=Category.FORENSICS,
        author="RickdeJager",
        version="0.6+",
        tags=["steganography", "steg", "crack", "hidden-data", "image"],
        tools=["stegseek"],
        offensive=False,
    )

    def options(self) -> list[Option]:
        from entr0py.core.wordlists import default_path
        return [
            Option("image",    "",    "Stego image file (JPEG)"),
            Option("wordlist", "",    "Wordlist for cracking",
                   required=False, default=default_path("passwords") or "/usr/share/wordlists/rockyou.txt"),
            Option("output",   "-xf", "Extract to file",
                   required=False, default="stegseek_out"),
            Option("crack",    "--crack", "Just crack, don't extract",
                   type=OptionType.BOOLEAN, required=False, default=False),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = ["stegseek", opts["image"], opts.get("wordlist", "/usr/share/wordlists/rockyou.txt")]
        if opts.get("output"):
            cmd += ["-xf", opts["output"]]
        if opts.get("crack"):
            cmd.append("--crack")
        async for line in self._exec(cmd):
            yield line
