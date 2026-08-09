"""entr0py.modules.web.wafw00f — Web Application Firewall (WAF) detection."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Wafw00f(Module):
    meta = ModuleMeta(
        name="wafw00f",
        slug="wafw00f",
        description=(
            "Identify and fingerprint WAF products protecting a web application. "
            "Detects 180+ WAFs including Cloudflare, Akamai, AWS WAF, ModSecurity."
        ),
        category=Category.WEB,
        author="EnableSecurity",
        version="2.x",
        tags=["waf", "fingerprint", "detection", "bypass"],
        packages=["wafw00f"],
        tools=["wafw00f"],
    )

    def options(self) -> list[Option]:
        return [
            Option("url",    "",    "Target URL"),
            Option("all",    "-a",  "Try to detect all WAFs (not just the first)",
                   type=OptionType.BOOLEAN, required=False, default=False),
            Option("output", "-o",  "Output file", required=False, default=""),
            Option("format", "-f",  "Output format (json|csv)",
                   required=False, default=""),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = ["wafw00f", opts["url"]]
        if opts.get("all"):
            cmd.append("-a")
        if opts.get("output"):
            cmd += ["-o", opts["output"]]
        if opts.get("format"):
            cmd += ["-f", opts["format"]]
        async for line in self._exec(cmd):
            yield line
