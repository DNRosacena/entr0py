"""entr0py.modules.mobile.apktool — Decode/rebuild APK resources and smali."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Apktool(Module):
    meta = ModuleMeta(
        name="Apktool",
        slug="apktool",
        description=(
            "Decode Android APKs to near-original form: AndroidManifest.xml, resources, "
            "and smali disassembly — the starting point for static APK analysis."
        ),
        category=Category.MOBILE,
        author="iBotPeaches",
        version="2.x",
        tags=["android", "apk", "decompile", "smali", "static-analysis"],
        tools=["apktool"],
        offensive=False,   # operates on a local APK you already hold — no live target
    )

    def options(self) -> list[Option]:
        return [
            Option("apk",    "",   "Path to the target .apk file"),
            Option("output", "-o", "Output directory (default: <apk-name>)",
                   required=False, default=""),
            Option("force",  "-f", "Overwrite the output directory if it exists",
                   type=OptionType.BOOLEAN, required=False, default=True),
            Option("no_src", "-s", "Skip smali disassembly (resources only, faster)",
                   type=OptionType.BOOLEAN, required=False, default=False),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = ["apktool", "d", opts["apk"]]
        if opts.get("output"):
            cmd += ["-o", opts["output"]]
        if opts.get("force"):
            cmd.append("-f")
        if opts.get("no_src"):
            cmd.append("-s")
        yield f"[*] Decoding {opts['apk']} with apktool…"
        async for line in self._exec(cmd):
            yield line
