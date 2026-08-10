"""entr0py.modules.mobile.jadx — Decompile an APK/DEX to readable Java/Kotlin."""
from __future__ import annotations

import json
import urllib.request
import zipfile
from typing import Any, AsyncIterator

from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType
from entr0py.core.paths import TOOLS_DIR


class Jadx(Module):
    meta = ModuleMeta(
        name="jadx",
        slug="jadx",
        description=(
            "Decompile Android APK/DEX bytecode back to readable Java and Kotlin source "
            "for reviewing app logic, hardcoded secrets, and API endpoints."
        ),
        category=Category.MOBILE,
        author="skylot",
        version="1.x",
        tags=["android", "apk", "dex", "decompile", "java", "static-analysis"],
        tools=["jadx"],
        offensive=False,
    )

    def options(self) -> list[Option]:
        return [
            Option("apk",     "",   "Path to the target .apk / .dex file"),
            Option("output",  "-d", "Output source directory",
                   required=False, default="jadx_out"),
            Option("threads", "-j", "Decompilation threads",
                   type=OptionType.INTEGER, required=False, default=0),
            Option("no_res",  "--no-res", "Skip resource decoding (source only)",
                   type=OptionType.BOOLEAN, required=False, default=False),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = ["jadx", "-d", opts.get("output", "jadx_out")]
        if opts.get("threads"):
            cmd += ["-j", str(opts["threads"])]
        if opts.get("no_res"):
            cmd.append("--no-res")
        cmd.append(opts["apk"])
        yield f"[*] Decompiling {opts['apk']} with jadx…"
        async for line in self._exec(cmd):
            yield line

    async def install(self) -> AsyncIterator[str]:
        """
        jadx ships as a release zip (bin/ + lib/), not a single binary — the generic
        installer can't handle it, so fetch + unpack here and drop a launcher on PATH.
        """
        launcher = TOOLS_DIR / "jadx"  # a `jadx` launcher on PATH → the real bin
        try:
            yield "[jadx] Fetching latest release from GitHub…"
            req = urllib.request.Request(
                "https://api.github.com/repos/skylot/jadx/releases/latest",
                headers={"User-Agent": "entr0py"},
            )
            with urllib.request.urlopen(req, timeout=15) as r:
                rel = json.loads(r.read())
            asset = next(
                (a for a in rel.get("assets", [])
                 if a["name"].startswith("jadx-") and a["name"].endswith(".zip")
                 and "gui" not in a["name"]),
                None,
            )
            if not asset:
                yield "[!] No jadx CLI zip found in the latest release."
                return
            TOOLS_DIR.mkdir(parents=True, exist_ok=True)
            zip_path = TOOLS_DIR / asset["name"]
            yield f"[jadx] Downloading {asset['name']}…"
            urllib.request.urlretrieve(asset["browser_download_url"], zip_path)
            jadx_home = TOOLS_DIR / "jadx-home"
            with zipfile.ZipFile(zip_path) as zf:
                zf.extractall(jadx_home)
            zip_path.unlink(missing_ok=True)
            bin_jadx = jadx_home / "bin" / "jadx"
            bin_jadx.chmod(0o755)
            # Launcher named `jadx` in TOOLS_DIR (on PATH via setup_env) → real bin
            launcher.write_text(f'#!/bin/sh\nexec "{bin_jadx}" "$@"\n')
            launcher.chmod(0o755)
            yield f"[+] jadx installed → {bin_jadx} (launcher: {launcher})"
        except Exception as exc:  # noqa: BLE001 — surface any download/extract failure
            yield f"[!] jadx install failed: {exc}"
            yield "    Manual: download from https://github.com/skylot/jadx/releases"
