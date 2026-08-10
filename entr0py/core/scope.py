"""
entr0py.core.scope
~~~~~~~~~~~~~~~~~~
Scope enforcement: before any offensive module runs, the target must be
declared inside the active session's scope.

Usage
-----
    scope = Scope()
    scope.add("192.168.1.0/24")
    scope.add("example.com")

    scope.check("192.168.1.42")     # ok — returns None
    scope.check("8.8.8.8")          # raises ScopeViolation (or warns)
"""
from __future__ import annotations

import ipaddress
import re

from entr0py.core.config import get as get_cfg


class ScopeViolation(Exception):
    """Raised when a target is outside the declared scope."""


_IPNet  = ipaddress.IPv4Network | ipaddress.IPv6Network
_IPAddr = ipaddress.IPv4Address | ipaddress.IPv6Address


class Scope:
    def __init__(self) -> None:
        self._networks: list[_IPNet]  = []
        self._domains:  list[str]     = []   # exact or *.wildcard

    # ------------------------------------------------------------------
    # Building the scope
    # ------------------------------------------------------------------

    def add(self, entry: str) -> None:
        """Add an IP, CIDR range, domain, or *.wildcard to scope."""
        entry = entry.strip()
        try:
            self._networks.append(ipaddress.ip_network(entry, strict=False))
            return
        except ValueError:
            pass
        self._domains.append(entry.lower())

    def clear(self) -> None:
        self._networks.clear()
        self._domains.clear()

    def is_empty(self) -> bool:
        return not self._networks and not self._domains

    def entries(self) -> list[str]:
        return [str(n) for n in self._networks] + list(self._domains)

    # ------------------------------------------------------------------
    # Checking
    # ------------------------------------------------------------------

    def _ip_in_scope(self, addr: _IPAddr) -> bool:
        return any(addr in net for net in self._networks)

    def _domain_in_scope(self, host: str) -> bool:
        host = host.lower()
        for d in self._domains:
            if d.startswith("*."):
                # wildcard: *.example.com matches a.example.com but not example.com
                suffix = d[2:]
                if host.endswith("." + suffix):
                    return True
            elif host == d or host.endswith("." + d):
                return True
        return False

    def _in_scope(self, target: str) -> bool:
        try:
            addr = ipaddress.ip_address(target)
            return self._ip_in_scope(addr)
        except ValueError:
            pass
        # Strip port if present
        host = re.sub(r":\d+$", "", target)
        # Strip scheme
        host = re.sub(r"^https?://", "", host)
        return self._domain_in_scope(host)

    def check(self, target: str) -> None:
        """
        Enforce scope rules.

        - Empty scope → always pass (scope is opt-in, not mandatory).
        - Scope defined + target inside → pass.
        - Scope defined + target outside → warn or raise depending on warn_only.
        """
        # No scope set: run freely.
        if self.is_empty():
            return

        if not self._in_scope(target):
            cfg = get_cfg()["scope"]
            warn_only = cfg.get("warn_only", True)
            msg = f"[!] '{target}' is outside your defined scope."
            if warn_only:
                print(msg + " Proceeding anyway (warn_only=true).")
                return
            raise ScopeViolation(msg + f" Add it with: entr0py scope add {target}")


# Process-wide default scope (populated per session)
_active: Scope = Scope()


def active() -> Scope:
    return _active


def reset() -> None:
    _active.clear()
