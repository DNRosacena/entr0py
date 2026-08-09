"""entr0py.modules.mobile.dex2jar — Convert APK/DEX to a .jar for JVM decompilers."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Dex2jar(Module):
    meta = ModuleMeta(
        name="dex2jar",
        slug="dex2jar",
        description=(
            "Convert Android Dalvik (.dex/.apk) bytecode into a standard .jar so it can "
            "be opened in JVM decompilers/analyzers (JD-GUI, procyon, etc.)."
        ),
        category=Category.MOBILE,
        author="pxb1988",
        version="2.x",
        tags=["android", "apk", "dex", "jar", "bytecode", "static-analysis"],
        # apt `dex2jar` ships several d2j-* wrappers; a stable `d2j-dex2jar` is ensured
        # on PATH in the image (symlinked if the package names it d2j-dex2jar.sh).
        tools=["d2j-dex2jar"],
        offensive=False,
    )

    def options(self) -> list[Option]:
        return [
            Option("apk",    "",   "Path to the target .apk / .dex file"),
            Option("output", "-o", "Output .jar path (default: <apk-name>-dex2jar.jar)",
                   required=False, default=""),
            Option("force",  "-f", "Overwrite the output file if it exists",
                   type=OptionType.BOOLEAN, required=False, default=True),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = ["d2j-dex2jar", opts["apk"]]
        if opts.get("output"):
            cmd += ["-o", opts["output"]]
        if opts.get("force"):
            cmd.append("-f")
        yield f"[*] Converting {opts['apk']} to a .jar with dex2jar…"
        async for line in self._exec(cmd):
            yield line
