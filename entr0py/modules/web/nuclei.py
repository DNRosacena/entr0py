"""entr0py.modules.web.nuclei — Template-based vulnerability scanner.

Replaces: changeme (unmaintained default-creds scanner)
Why better: 9000+ community templates covering CVEs, misconfigs, default creds,
            exposures, OSINT, and more.  Actively maintained by ProjectDiscovery.
"""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Nuclei(Module):
    meta = ModuleMeta(
        name="Nuclei",
        slug="nuclei",
        description=(
            "Fast, template-based vulnerability scanner with 9000+ community templates. "
            "Covers CVEs, misconfigs, default credentials, exposures, and more."
        ),
        category=Category.WEB,
        author="ProjectDiscovery",
        version="3.x",
        tags=["vuln-scan", "cve", "templates", "misconfig", "default-creds", "exposure"],
        tools=["nuclei"],
        replaces=["changeme"],
    )

    def options(self) -> list[Option]:
        return [
            Option("target",      "-u",   "Target URL or IP"),
            Option("list",        "-l",   "File with list of targets",
                   required=False, default=""),
            Option("templates",   "-t",   "Template path/tag (e.g. cves/ or default-logins)",
                   required=False, default=""),
            Option("severity",    "-s",   "Severity filter (info,low,medium,high,critical)",
                   required=False, default="medium,high,critical"),
            Option("tags",        "-tags","Template tags filter (e.g. xss,sqli)",
                   required=False, default=""),
            Option("rate_limit",  "-rl",  "Requests per second",
                   type=OptionType.INTEGER, required=False, default=150),
            Option("concurrency", "-c",   "Template concurrency",
                   type=OptionType.INTEGER, required=False, default=25),
            Option("output",      "-o",   "Output file",
                   required=False, default="nuclei_out.txt"),
            Option("json",        "-json","JSON output",
                   type=OptionType.BOOLEAN, required=False, default=False),
            Option("update_templates", "-ut", "Update templates before scan",
                   type=OptionType.BOOLEAN, required=False, default=False),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        # Update templates if requested
        if opts.get("update_templates"):
            yield "[*] Updating nuclei templates…"
            async for line in self._exec(["nuclei", "-ut"]):
                yield line

        cmd = ["nuclei", "-nc"]   # -nc = no color (cleaner pipe output)
        if opts.get("list"):
            cmd += ["-l", opts["list"]]
        else:
            cmd += ["-u", opts["target"]]
        if opts.get("templates"):
            cmd += ["-t", opts["templates"]]
        if opts.get("severity"):
            cmd += ["-s", opts["severity"]]
        if opts.get("tags"):
            cmd += ["-tags", opts["tags"]]
        cmd += ["-rl", str(opts.get("rate_limit", 150))]
        cmd += ["-c",  str(opts.get("concurrency", 25))]
        if opts.get("output"):
            cmd += ["-o", opts["output"]]
        if opts.get("json"):
            cmd.append("-json")
        async for line in self._exec(cmd):
            yield line
