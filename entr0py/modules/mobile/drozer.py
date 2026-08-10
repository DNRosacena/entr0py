"""entr0py.modules.mobile.drozer — Android app attack-surface assessment."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option


class Drozer(Module):
    meta = ModuleMeta(
        name="drozer",
        slug="drozer",
        description=(
            "Assess an Android app's attack surface — exported activities, services, "
            "broadcast receivers, content providers, and IPC. Needs the drozer agent app "
            "running on a device/emulator, reached over adb."
        ),
        category=Category.MOBILE,
        author="WithSecureLabs",
        version="3.x",
        tags=["android", "attack-surface", "ipc", "content-provider", "dynamic"],
        tools=["drozer"],
        packages=["drozer"],
        offensive=False,   # tests apps on a device you control; no network target to scope
    )

    def options(self) -> list[Option]:
        return [
            Option("server",  "--server", "Agent host (adb-forwarded device); blank = 127.0.0.1",
                   required=False, default=""),
            Option("command", "-c",
                   "Single drozer command (e.g. 'run app.package.list'); blank = interactive console",
                   required=False, default=""),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        yield "[*] drozer needs the agent app running on a device/emulator with its server on."
        yield "    Bridge it first:  adb forward tcp:31415 tcp:31415"
        cmd = ["drozer", "console", "connect"]
        if opts.get("server"):
            cmd += ["--server", opts["server"]]
        if opts.get("command"):
            cmd += ["-c", opts["command"]]
        async for line in self._exec(cmd):
            yield line
