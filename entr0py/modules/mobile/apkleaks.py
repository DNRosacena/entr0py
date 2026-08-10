"""entr0py.modules.mobile.apkleaks — Scan an APK for secrets, URIs, and endpoints."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option


class Apkleaks(Module):
    meta = ModuleMeta(
        name="APKLeaks",
        slug="apkleaks",
        description=(
            "Scan an APK for leaked secrets: API keys, tokens, URIs, S3 buckets, and "
            "endpoints. Decompiles with jadx under the hood, then regex-matches."
        ),
        category=Category.MOBILE,
        author="dwisiswant0",
        version="2.x",
        tags=["android", "apk", "secrets", "api-keys", "endpoints", "static-analysis"],
        tools=["apkleaks"],
        packages=["apkleaks"],   # pip package; jadx must also be present (its backend)
        offensive=False,
    )

    def options(self) -> list[Option]:
        return [
            Option("apk",     "-f", "Path to the target .apk file"),
            Option("output",  "-o", "Output results file",
                   required=False, default="apkleaks_out.txt"),
            Option("pattern", "-p", "Custom JSON pattern file (extra regexes)",
                   required=False, default=""),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = ["apkleaks", "-f", opts["apk"]]
        if opts.get("output"):
            cmd += ["-o", opts["output"]]
        if opts.get("pattern"):
            cmd += ["-p", opts["pattern"]]
        yield f"[*] Scanning {opts['apk']} for leaked secrets/endpoints…"
        async for line in self._exec(cmd):
            yield line
