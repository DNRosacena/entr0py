"""entr0py.modules.web.sqlmap — Automatic SQL injection detection and exploitation."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Sqlmap(Module):
    meta = ModuleMeta(
        name="sqlmap",
        slug="sqlmap",
        description=(
            "Automatic SQL injection and database takeover tool supporting MySQL, "
            "PostgreSQL, Oracle, MSSQL, SQLite, and more. Detects and exploits."
        ),
        category=Category.WEB,
        author="sqlmapproject",
        version="1.8+",
        tags=["sqli", "sql-injection", "database", "exploitation"],
        packages=["sqlmap"],
        tools=["sqlmap"],
    )

    def options(self) -> list[Option]:
        return [
            Option("url",      "-u",       "Target URL with parameter (e.g. http://site.com/page?id=1)"),
            Option("dbs",      "--dbs",    "Enumerate databases",
                   type=OptionType.BOOLEAN, required=False, default=False),
            Option("dump",     "--dump",   "Dump database table contents",
                   type=OptionType.BOOLEAN, required=False, default=False),
            Option("level",    "--level",  "Test level 1-5 (default 1)",
                   type=OptionType.INTEGER, required=False, default=1),
            Option("risk",     "--risk",   "Risk level 1-3 (default 1)",
                   type=OptionType.INTEGER, required=False, default=1),
            Option("technique","--technique", "SQLi technique(s) (B,E,U,S,T,Q)",
                   required=False, default="BEUSTQ"),
            Option("dbms",     "--dbms",   "Force backend DBMS (mysql, postgresql, …)",
                   required=False, default=""),
            Option("batch",    "--batch",  "Non-interactive (auto answer defaults)",
                   type=OptionType.BOOLEAN, required=False, default=True),
            Option("threads",  "--threads","Concurrency (1-10)",
                   type=OptionType.INTEGER, required=False, default=5),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = ["sqlmap", "-u", opts["url"]]
        if opts.get("dbs"):
            cmd.append("--dbs")
        if opts.get("dump"):
            cmd.append("--dump")
        cmd += ["--level", str(opts.get("level", 1))]
        cmd += ["--risk",  str(opts.get("risk", 1))]
        cmd += ["--technique", opts.get("technique", "BEUSTQ")]
        if opts.get("dbms"):
            cmd += ["--dbms", opts["dbms"]]
        if opts.get("batch", True):
            cmd.append("--batch")
        cmd += ["--threads", str(opts.get("threads", 5))]
        async for line in self._exec(cmd):
            yield line
