"""
entr0py.core.paths
~~~~~~~~~~~~~~~~~~
Single source of truth for all entr0py data paths.

On Windows the base directory defaults to D:/entr0py so nothing ends up
on the crowded C: drive.  On Linux/macOS it defaults to ~/.entr0py.
The base can be overridden by setting the ENTR0PY_DATA_DIR environment
variable or by changing [framework] data_dir in config/default.toml.
"""
from __future__ import annotations

import os
import platform
from pathlib import Path


def _base() -> Path:
    # 1. Explicit environment variable override
    env = os.environ.get("ENTR0PY_DATA_DIR")
    if env:
        return Path(env)

    # 2. Windows → D: drive
    if platform.system().lower().startswith("win"):
        return Path("D:/entr0py")

    # 3. Linux / macOS
    return Path.home() / ".entr0py"


DATA_DIR      = _base()
TOOLS_DIR     = DATA_DIR / "tools"
WORDLISTS_DIR = DATA_DIR / "wordlists"
OUTPUT_DIR    = DATA_DIR / "output"
SESSIONS_DB   = DATA_DIR / "sessions.db"
CONFIG_FILE   = DATA_DIR / "config.toml"   # user config overrides

# Go and Cargo also live on the same drive so installs don't touch C:
GO_DIR        = DATA_DIR / "go"
GO_BIN        = GO_DIR / "bin"
CARGO_DIR     = DATA_DIR / "cargo"
CARGO_BIN     = CARGO_DIR / "bin"


def setup_env() -> None:
    """
    Prepend all entr0py bin directories to PATH so that previously installed
    tools are found by shutil.which() on every startup — not just right after
    install.  Safe to call multiple times (idempotent).
    """
    import os

    # Standard Go install location (winget / system installer)
    std_go = Path(os.environ.get("PROGRAMFILES", "C:/Program Files")) / "Go" / "bin"

    dirs_to_add = [
        GO_BIN,       # D:/entr0py/go/bin       (zip-installed Go tools / go install)
        CARGO_BIN,    # D:/entr0py/cargo/bin     (cargo install)
        TOOLS_DIR,    # D:/entr0py/tools         (GitHub release binaries, pspy, etc.)
        std_go,       # C:/Program Files/Go/bin  (winget-installed Go)
    ]

    current = os.environ.get("PATH", "")
    prepend = os.pathsep.join(
        str(d) for d in dirs_to_add
        if d.exists() and str(d) not in current
    )
    if prepend:
        os.environ["PATH"] = prepend + os.pathsep + current

    # Point Go and Cargo at our D: directories so new installs stay there
    os.environ.setdefault("GOPATH",     str(GO_DIR))
    os.environ.setdefault("GOBIN",      str(GO_BIN))
    os.environ.setdefault("CARGO_HOME", str(CARGO_DIR))
