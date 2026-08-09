"""
entr0py.core.base
~~~~~~~~~~~~~~~~~
Foundation classes: Category, Option, ModuleMeta, and the abstract Module.

Every tool in entr0py is a Module subclass.  Subclasses must:
  - define a class-level ``meta: ModuleMeta`` attribute
  - implement ``async def run(self, opts) -> AsyncIterator[str]``
  - optionally override ``options()`` and ``install()``
"""
from __future__ import annotations

import asyncio
import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncIterator


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------

class Category(str, Enum):
    RECON        = "recon"
    OSINT        = "osint"
    NETWORK      = "network"
    WEB          = "web"
    PASSWORDS    = "passwords"
    EXPLOITATION = "exploitation"
    POST_EXPLOIT = "post_exploit"
    WIRELESS     = "wireless"
    FORENSICS    = "forensics"
    SOCIAL       = "social"
    MOBILE       = "mobile"

    @property
    def label(self) -> str:
        return {
            "recon":        "Reconnaissance",
            "osint":        "OSINT",
            "network":      "Network",
            "web":          "Web Applications",
            "passwords":    "Passwords & Hashes",
            "exploitation": "Exploitation",
            "post_exploit": "Post-Exploitation",
            "wireless":     "Wireless",
            "forensics":    "Forensics",
            "social":       "Social Engineering",
            "mobile":       "Mobile (APK Analysis)",
        }[self.value]

    @property
    def icon(self) -> str:
        return {
            "recon":        "󰈈",
            "osint":        "󰛐",
            "network":      "󰛳",
            "web":          "󰖟",
            "passwords":    "󰌋",
            "exploitation": "󱒉",
            "post_exploit": "󰓾",
            "wireless":     "󰀂",
            "forensics":    "󰍔",
            "social":       "󰀄",
            "mobile":       "󰀲",
        }[self.value]


# ---------------------------------------------------------------------------
# Option
# ---------------------------------------------------------------------------

class OptionType(str, Enum):
    STRING  = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    FILE    = "file"
    CHOICE  = "choice"


@dataclass
class Option:
    name: str
    flag: str                               # CLI flag(s), e.g. "-u" / "--url"
    description: str
    type: OptionType       = OptionType.STRING
    required: bool         = True
    default: Any           = None
    choices: list[str]     = field(default_factory=list)

    def prompt_label(self) -> str:
        suffix = "[required]" if self.required else f"[optional, default: {self.default}]"
        return f"  {self.name} {suffix} — {self.description}"


# ---------------------------------------------------------------------------
# ModuleMeta
# ---------------------------------------------------------------------------

@dataclass
class ModuleMeta:
    name: str                               # Display name
    slug: str                               # Unique key, e.g. "subfinder"
    description: str
    category: Category
    author: str
    version: str
    tags: list[str]             = field(default_factory=list)
    tools: list[str]            = field(default_factory=list)   # system binaries
    packages: list[str]         = field(default_factory=list)   # pip packages
    repos: dict[str, str]       = field(default_factory=dict)   # {name: git_url}
    offensive: bool             = True    # requires scope check before running
    replaces: list[str]         = field(default_factory=list)   # fsociety equivalents


# ---------------------------------------------------------------------------
# Module (abstract base)
# ---------------------------------------------------------------------------

class Module(ABC):
    """Base class for all entr0py modules."""

    meta: ModuleMeta  # must be set on the concrete subclass

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def options(self) -> list[Option]:
        """Return configurable options.  Override in subclass."""
        return []

    def is_installed(self) -> bool:
        """True if all required system binaries are on PATH or in TOOLS_DIR."""
        from entr0py.core.paths import TOOLS_DIR, GO_BIN, CARGO_BIN
        import platform
        is_win = platform.system().lower().startswith("win")

        def _found(tool: str) -> bool:
            if shutil.which(tool):
                return True
            # Check our local install dirs directly (tools not yet in PATH)
            suffixes = [".exe", ""] if is_win else [""]
            for d in (TOOLS_DIR, GO_BIN, CARGO_BIN):
                for sfx in suffixes:
                    if (d / (tool + sfx)).exists():
                        return True
            return False

        return all(_found(t) for t in self.meta.tools)

    async def install(self) -> AsyncIterator[str]:
        """
        Yield status lines while installing dependencies.
        Default: no-op — the generic installer in core.installer handles it.
        Override for special steps (e.g., go install, git clone + make).
        """
        yield f"[*] No custom install for {self.meta.name}. Run: entr0py install {self.meta.slug}"

    @abstractmethod
    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        """Stream output lines while executing the module."""
        ...

    # ------------------------------------------------------------------
    # Execution helpers
    # ------------------------------------------------------------------

    async def _exec(
        self,
        cmd: list[str],
        cwd: str | None = None,
        env:  dict[str, str] | None = None,
    ) -> AsyncIterator[str]:
        """Execute a subprocess and yield decoded output lines."""
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=cwd,
                env=env,
            )
        except FileNotFoundError:
            yield f"[!] Binary not found: {cmd[0]!r}. Run: entr0py install {self.meta.slug}"
            return

        assert proc.stdout
        async for raw in proc.stdout:
            yield raw.decode(errors="replace").rstrip()

        rc = await proc.wait()
        if rc not in (0, None):
            yield f"[!] {cmd[0]} exited with code {rc}"

    async def _exec_shell(
        self,
        command: str,
        cwd: str | None = None,
    ) -> AsyncIterator[str]:
        """Execute a shell string and yield output lines."""
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=cwd,
        )
        assert proc.stdout
        async for raw in proc.stdout:
            yield raw.decode(errors="replace").rstrip()
        await proc.wait()
