"""entr0py.modules.web.corsy — CORS misconfiguration scanner."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType
from entr0py.core.paths import TOOLS_DIR


class Corsy(Module):
    meta = ModuleMeta(
        name="Corsy",
        slug="corsy",
        description=(
            "Scan for Cross-Origin Resource Sharing (CORS) misconfigurations: "
            "wildcard origins, null origin bypass, trusted subdomain abuse, etc."
        ),
        category=Category.WEB,
        author="s0md3v",
        version="1.0+",
        tags=["cors", "misconfiguration", "web", "bypass"],
        repos={"Corsy": "https://github.com/s0md3v/Corsy"},
    )

    def options(self) -> list[Option]:
        return [
            Option("url",     "-u",  "Target URL",
                   required=False, default=""),
            Option("input",   "-i",  "Input file with list of URLs",
                   required=False, default=""),
            Option("threads", "-t",  "Threads",
                   type=OptionType.INTEGER, required=False, default=10),
            Option("output",  "-o",  "Output file (JSON)",
                   required=False, default="corsy_out.json"),
            Option("headers", "-H",  "Custom header string",
                   required=False, default=""),
            Option("quiet",   "-q",  "Quiet output",
                   type=OptionType.BOOLEAN, required=False, default=False),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        corsy_path = TOOLS_DIR / "Corsy" / "corsy.py"
        if not corsy_path.exists():
            yield "[!] Corsy not found. Run: entr0py install corsy"
            return

        import sys
        cmd = [sys.executable, str(corsy_path)]
        if opts.get("url"):
            cmd += ["-u", opts["url"]]
        elif opts.get("input"):
            cmd += ["-i", opts["input"]]
        else:
            yield "[!] Provide either 'url' or 'input' file."
            return
        cmd += ["-t", str(opts.get("threads", 10))]
        if opts.get("output"):
            cmd += ["-o", opts["output"]]
        if opts.get("headers"):
            cmd += ["-H", opts["headers"]]
        if opts.get("quiet"):
            cmd.append("-q")
        async for line in self._exec(cmd):
            yield line
