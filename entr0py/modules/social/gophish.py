"""entr0py.modules.social.gophish — Open-source phishing simulation platform."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Gophish(Module):
    meta = ModuleMeta(
        name="GoPhish",
        slug="gophish",
        description=(
            "Open-source phishing framework with a web UI: create email campaigns, "
            "track clicks/opens/submissions, and generate detailed reports."
        ),
        category=Category.SOCIAL,
        author="jordan-wright",
        version="0.12+",
        tags=["phishing", "email", "campaign", "tracking", "social-engineering"],
        tools=["gophish"],
    )

    def options(self) -> list[Option]:
        return [
            Option("config", "--config", "GoPhish config file",
                   required=False, default="config.json"),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = ["gophish"]
        if opts.get("config"):
            cmd += ["--config", opts["config"]]
        yield "[*] GoPhish admin interface will be available at https://localhost:3333"
        yield "[*] Default credentials: admin / gophish"
        async for line in self._exec(cmd):
            yield line
