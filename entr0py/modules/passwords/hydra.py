"""entr0py.modules.passwords.hydra — Multi-protocol online brute-force."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class Hydra(Module):
    meta = ModuleMeta(
        name="Hydra",
        slug="hydra",
        description=(
            "Fast, parallelized login cracker supporting 50+ protocols: "
            "SSH, FTP, HTTP, HTTPS, SMB, RDP, MySQL, MSSQL, VNC, and more."
        ),
        category=Category.PASSWORDS,
        author="van Hauser / THC",
        version="9.x",
        tags=["brute-force", "login", "credentials", "ssh", "ftp", "http"],
        tools=["hydra"],
    )

    def options(self) -> list[Option]:
        from entr0py.core.wordlists import default_path
        return [
            Option("target",    "",        "Target IP or hostname"),
            Option("service",   "",        "Service/protocol (ssh, ftp, http-post-form, rdp, …)"),
            Option("userlist",  "-L",      "Username wordlist file",
                   required=False, default=default_path("usernames")),
            Option("username",  "-l",      "Single username",
                   required=False, default=""),
            Option("passlist",  "-P",      "Password wordlist file",
                   required=False, default=default_path("passwords")),
            Option("password",  "-p",      "Single password",
                   required=False, default=""),
            Option("threads",   "-t",      "Threads per target",
                   type=OptionType.INTEGER, required=False, default=16),
            Option("port",      "-s",      "Custom port",
                   type=OptionType.INTEGER, required=False, default=0),
            Option("verbose",   "-V",      "Verbose (show all attempts)",
                   type=OptionType.BOOLEAN, required=False, default=False),
            Option("output",    "-o",      "Output file for found credentials",
                   required=False, default="hydra_found.txt"),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        cmd = ["hydra"]
        if opts.get("userlist"):
            cmd += ["-L", opts["userlist"]]
        elif opts.get("username"):
            cmd += ["-l", opts["username"]]
        if opts.get("passlist"):
            cmd += ["-P", opts["passlist"]]
        elif opts.get("password"):
            cmd += ["-p", opts["password"]]
        cmd += ["-t", str(opts.get("threads", 16))]
        if opts.get("port"):
            cmd += ["-s", str(opts["port"])]
        if opts.get("verbose"):
            cmd.append("-V")
        if opts.get("output"):
            cmd += ["-o", opts["output"]]
        cmd += [opts["target"], opts["service"]]
        async for line in self._exec(cmd):
            yield line
