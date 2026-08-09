"""
entr0py.core.installer
~~~~~~~~~~~~~~~~~~~~~~
Installs a module's dependencies.  Handles:
  - pip packages
  - Go binaries  (go install …@latest) — installs Go itself if missing
  - Rust binaries (cargo install) — installs rustup if missing
  - Ruby gems (gem install)
  - GitHub release binary downloads
  - apt / brew / pacman / dnf / winget system packages
  - git-clone repos + pip install -r requirements.txt
"""
from __future__ import annotations

import asyncio
import os
import platform
import shutil
import sys
import tempfile
from pathlib import Path
from typing import AsyncIterator

from entr0py.core.base import Module
from entr0py.core.paths import DATA_DIR, TOOLS_DIR, GO_BIN, GO_DIR, CARGO_BIN, CARGO_DIR


# ---------------------------------------------------------------------------
# Go tool install paths  (slug → go install path)
# ---------------------------------------------------------------------------
_GO_INSTALL: dict[str, str] = {
    "subfinder":    "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
    "httpx":        "github.com/projectdiscovery/httpx/cmd/httpx@latest",
    "dnsx":         "github.com/projectdiscovery/dnsx/cmd/dnsx@latest",
    "nuclei":       "github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest",
    "katana":       "github.com/projectdiscovery/katana/cmd/katana@latest",
    "amass":        "github.com/owasp-amass/amass/v4/...@latest",
    "ffuf":         "github.com/ffuf/ffuf/v2@latest",
    "dalfox":       "github.com/hahwul/dalfox/v2@latest",
    # phoneinfoga installed via GitHub releases (see _GH_RELEASES)
    "traitor":      "github.com/liamg/traitor@latest",
    "evilginx2":    "github.com/kgretzky/evilginx2@latest",
    "gophish":      "github.com/gophish/gophish@latest",
    "bettercap":    "github.com/bettercap/bettercap@latest",
}

# ---------------------------------------------------------------------------
# Rust (cargo) tools  (slug → crate name)
# ---------------------------------------------------------------------------
_CARGO_INSTALL: dict[str, str] = {
    "rustscan": "rustscan",
}

# ---------------------------------------------------------------------------
# Ruby gems  (slug → gem name)
# ---------------------------------------------------------------------------
_GEM_INSTALL: dict[str, str] = {
    "cewl":       "cewl",
    "whatweb":    "whatweb",
    "nikto":      "nikto",
    "metasploit": "metasploit",
}

# ---------------------------------------------------------------------------
# GitHub release binary downloads
# (slug → (repo, asset_pattern_linux, asset_pattern_darwin, asset_pattern_windows, binary_name))
# asset_pattern is matched against release asset filenames (substring match)
# ---------------------------------------------------------------------------
_GH_RELEASES: dict[str, dict] = {
    "pspy": {
        "repo":    "DominicBreuker/pspy",
        "linux":   "pspy64",
        "darwin":  "pspy64",
        "windows": None,
        "binary":  "pspy",
    },
    "linpeas": {
        "repo":    "carlospolop/PEASS-ng",
        "linux":   "linpeas.sh",
        "darwin":  "linpeas.sh",
        "windows": "winPEASx64.exe",
        "binary":  "linpeas",
    },
    "stegseek": {
        "repo":    "RickdeJager/stegseek",
        "linux":   ".deb",
        "darwin":  ".tar.gz",
        "windows": None,
        "binary":  "stegseek",
    },
    "phoneinfoga": {
        "repo":    "sundowndev/phoneinfoga",
        "linux":   "Linux_x86_64.tar.gz",
        "darwin":  "Darwin_x86_64.tar.gz",
        "windows": "Windows_x86_64.tar.gz",
        "binary":  "phoneinfoga",
    },
    "searchsploit": {
        "repo":    "offensive-security/exploit-database",
        "linux":   None,
        "darwin":  None,
        "windows": None,
        "binary":  "searchsploit",
    },
}

# ---------------------------------------------------------------------------
# pip packages  (slug → list of pip packages; empty = system-only)
# ---------------------------------------------------------------------------
_PIP_PACKAGES: dict[str, list[str]] = {
    "theharvester": ["theHarvester"],
    "sherlock":     ["sherlock-project"],
    "maigret":      ["maigret"],
    "holehe":       ["holehe"],
    "s3scanner":    ["s3scanner"],
    "sqlmap":       ["sqlmap"],
    "arjun":        ["arjun"],
    "wafw00f":      ["wafw00f"],
    "volatility3":  ["volatility3"],
    "wifite":       ["wifite2"],
}

# ---------------------------------------------------------------------------
# Git repos to clone  (slug → URL)
# ---------------------------------------------------------------------------
_GIT_REPOS: dict[str, str] = {
    "corsy":        "https://github.com/s0md3v/Corsy",
    "cupp":         "https://github.com/Mebus/cupp",
    "xsstrike":     "https://github.com/s0md3v/XSStrike",
    "searchsploit": "https://github.com/offensive-security/exploit-database",
}

# Tools that only work on Linux/macOS — skip install entirely on Windows
_LINUX_ONLY: set[str] = {
    "setoolkit", "aircrack", "wifite", "hcxdumptool", "kismet",
    "netdiscover", "linpeas", "pspy", "mimikatz",
}

# ---------------------------------------------------------------------------
# apt package name overrides  (binary → apt package)
# ---------------------------------------------------------------------------
_APT_PKG: dict[str, str] = {
    "exiftool":       "libimage-exiftool-perl",
    "aircrack-ng":    "aircrack-ng",
    "airodump-ng":    "aircrack-ng",
    "aireplay-ng":    "aircrack-ng",
    "airmon-ng":      "aircrack-ng",
    "hcxdumptool":    "hcxdumptool",
    "hcxpcapngtool":  "hcxtools",
    "kismet":         "kismet",
    "wifite":         "wifite",
    "hydra":          "hydra",
    "john":           "john",
    "hashcat":        "hashcat",
    "nikto":          "nikto",
    "sqlmap":         "sqlmap",
    "stegseek":       "stegseek",
    "steghide":       "steghide",
    "binwalk":        "binwalk",
    "foremost":       "foremost",
    "masscan":        "masscan",
    "netdiscover":    "netdiscover",
    "nmap":           "nmap",
    "crunch":         "crunch",
    "git":            "git",
    "curl":           "curl",
    "wget":           "wget",
    "nc":             "netcat-openbsd",
    "netcat":         "netcat-openbsd",
    "msfconsole":     "metasploit-framework",
    "searchsploit":   "exploitdb",
    "setoolkit":      "set",
    "set":            "set",
    "gem":            "ruby",
    "ruby":           "ruby",
    "cargo":          "cargo",
    "rustup":         "rustup",
}

_BREW_PKG: dict[str, str] = {
    "exiftool":    "exiftool",
    "aircrack-ng": "aircrack-ng",
    "hydra":       "hydra",
    "john":        "john",
    "hashcat":     "hashcat",
    "nikto":       "nikto",
    "sqlmap":      "sqlmap",
    "binwalk":     "binwalk",
    "masscan":     "masscan",
    "nmap":        "nmap",
    "crunch":      "crunch",
    "wget":        "wget",
    "ruby":        "ruby",
    "cargo":       "rust",
    "gem":         "ruby",
}

_WINGET_PKG: dict[str, str] = {
    "nmap":      "Insecure.Nmap",
    "wireshark": "WiresharkFoundation.Wireshark",
    "git":       "Git.Git",
    "curl":      "cURL.cURL",
    "wget":      "JernejSimoncic.Wget",
    "hashcat":   "Hashcat.Hashcat",
    "ruby":      "RubyInstallerTeam.Ruby",
    "rustup":    "Rustlang.Rustup",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _run(cmd: list[str], env: dict | None = None) -> AsyncIterator[str]:
    merged_env = {**os.environ, **(env or {})}
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            env=merged_env,
        )
    except FileNotFoundError:
        yield f"[!] Command not found: {cmd[0]!r}"
        return
    assert proc.stdout
    async for raw in proc.stdout:
        yield raw.decode(errors="replace").rstrip()
    await proc.wait()


def _system() -> str:
    s = platform.system().lower()
    if s.startswith("win"):
        return "windows"
    if s == "darwin":
        return "darwin"
    return "linux"


def _pkg_manager() -> str | None:
    for mgr in ("apt-get", "apt", "pacman", "dnf", "yum", "brew", "winget"):
        if shutil.which(mgr):
            return mgr
    return None


def _ensure_go_in_path() -> None:
    go_bin = str(GO_BIN)
    if go_bin not in os.environ.get("PATH", ""):
        os.environ["PATH"] = go_bin + os.pathsep + os.environ.get("PATH", "")
    # Also set GOPATH so go install writes to our D: directory
    os.environ.setdefault("GOPATH", str(GO_DIR))


def _ensure_cargo_in_path() -> None:
    cargo_bin = str(CARGO_BIN)
    if cargo_bin not in os.environ.get("PATH", ""):
        os.environ["PATH"] = cargo_bin + os.pathsep + os.environ.get("PATH", "")
    os.environ.setdefault("CARGO_HOME", str(CARGO_DIR))


# ---------------------------------------------------------------------------
# Go installation
# ---------------------------------------------------------------------------

async def _install_go_zip_windows() -> AsyncIterator[str]:
    """
    Extract Go zip directly into GO_DIR (D:/entr0py/go).
    No admin rights or installer policies needed.
    """
    import urllib.request, zipfile
    yield "[go] Fetching latest Go version from go.dev …"
    try:
        with urllib.request.urlopen("https://go.dev/VERSION?m=text", timeout=10) as r:
            go_ver = r.read().decode().strip().split("\n")[0]
    except Exception as exc:
        yield f"[!] Could not fetch Go version: {exc}"
        return

    arch_map = {"AMD64": "amd64", "x86": "386", "ARM64": "arm64"}
    arch = arch_map.get(platform.machine().upper(), "amd64")
    zip_name = f"{go_ver}.windows-{arch}.zip"
    url = f"https://go.dev/dl/{zip_name}"

    yield f"[go] Downloading {zip_name} to D: …"
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp) / zip_name
        try:
            urllib.request.urlretrieve(url, dest)
        except Exception as exc:
            yield f"[!] Download failed: {exc}"
            return

        yield f"[go] Extracting to {GO_DIR.parent} …"
        # zip contains a top-level "go/" folder — extract parent so it lands at GO_DIR
        GO_DIR.parent.mkdir(parents=True, exist_ok=True)
        if GO_DIR.exists():
            import shutil as _sh
            _sh.rmtree(GO_DIR)
        try:
            with zipfile.ZipFile(dest) as zf:
                zf.extractall(GO_DIR.parent)
            # The zip extracts as "go/" — rename if needed to match GO_DIR name
            extracted = GO_DIR.parent / "go"
            if extracted.exists() and extracted != GO_DIR:
                extracted.rename(GO_DIR)
        except Exception as exc:
            yield f"[!] Extraction failed: {exc}"
            return

    go_bin = str(GO_BIN)
    if go_bin not in os.environ.get("PATH", ""):
        os.environ["PATH"] = go_bin + os.pathsep + os.environ.get("PATH", "")
    yield f"[go] Go {go_ver} installed to {GO_DIR}"
    yield f"[go] Added {GO_BIN} to PATH"


async def _install_go() -> AsyncIterator[str]:
    sys_name = _system()
    yield "[go] Go not found — attempting automatic installation…"

    if sys_name == "windows":
        if shutil.which("winget"):
            yield "[go] Installing Go via winget…"
            async for line in _run(["winget", "install", "--id", "GoLang.Go", "-e", "--silent"]):
                yield line
            # winget installs to C:\Program Files\Go — add that to PATH too
            new_go = Path(os.environ.get("PROGRAMFILES", "C:\\Program Files")) / "Go" / "bin"
            if new_go.exists() and str(new_go) not in os.environ.get("PATH", ""):
                os.environ["PATH"] = str(new_go) + os.pathsep + os.environ.get("PATH", "")
                yield f"[go] Added {new_go} to PATH"
        else:
            # No winget — extract zip directly to D:/entr0py/go (no admin needed)
            async for line in _install_go_zip_windows():
                yield line
        return

    if sys_name == "darwin":
        if shutil.which("brew"):
            yield "[go] Installing Go via brew…"
            async for line in _run(["brew", "install", "go"]):
                yield line
            return
        yield "[!] Homebrew not found. Download Go from https://go.dev/dl/"
        return

    # Linux: download tarball
    import urllib.request
    yield "[go] Fetching latest Go version…"
    try:
        with urllib.request.urlopen("https://go.dev/VERSION?m=text", timeout=10) as r:
            go_ver = r.read().decode().strip().split("\n")[0]
    except Exception as exc:
        yield f"[!] Could not fetch Go version: {exc}"
        yield "[!] Install Go manually from https://go.dev/dl/"
        return

    arch_map = {"x86_64": "amd64", "aarch64": "arm64", "armv7l": "armv6l"}
    arch = arch_map.get(platform.machine(), platform.machine())
    tarball = f"{go_ver}.linux-{arch}.tar.gz"
    url = f"https://go.dev/dl/{tarball}"
    yield f"[go] Downloading {url} …"

    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp) / tarball
        try:
            urllib.request.urlretrieve(url, dest)
        except Exception as exc:
            yield f"[!] Download failed: {exc}"
            return
        yield "[go] Extracting to /usr/local/go …"
        async for line in _run(["sudo", "rm", "-rf", "/usr/local/go"]):
            yield line
        async for line in _run(["sudo", "tar", "-C", "/usr/local", "-xzf", str(dest)]):
            yield line

    go_usr_bin = "/usr/local/go/bin"
    os.environ["PATH"] = go_usr_bin + os.pathsep + os.environ.get("PATH", "")
    yield f"[go] Go {go_ver} installed. Add 'export PATH=$PATH:/usr/local/go/bin' to ~/.bashrc"


# ---------------------------------------------------------------------------
# Rust / cargo installation
# ---------------------------------------------------------------------------

async def _install_rust() -> AsyncIterator[str]:
    sys_name = _system()
    yield "[rust] Rust/cargo not found — installing via rustup…"

    if sys_name == "windows":
        if shutil.which("winget"):
            yield "[rust] Installing rustup via winget…"
            async for line in _run(["winget", "install", "--id", "Rustlang.Rustup", "-e", "--silent"]):
                yield line
            _ensure_cargo_in_path()
            return
        yield "[!] Download rustup from https://rustup.rs/"
        return

    # macOS / Linux: curl | sh
    import urllib.request
    yield "[rust] Running rustup installer (non-interactive)…"
    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / "rustup.sh"
        try:
            urllib.request.urlretrieve("https://sh.rustup.rs", script)
        except Exception as exc:
            yield f"[!] Could not download rustup: {exc}"
            return
        async for line in _run(["sh", str(script), "-y", "--no-modify-path"]):
            yield line
    _ensure_cargo_in_path()
    yield f"[rust] Cargo available at {CARGO_BIN}"


# ---------------------------------------------------------------------------
# GitHub releases binary download
# ---------------------------------------------------------------------------

async def _install_gh_release(slug: str) -> AsyncIterator[str]:
    info = _GH_RELEASES.get(slug)
    if not info:
        return

    sys_name = _system()
    asset_pattern = info.get(sys_name)
    if not asset_pattern:
        yield f"[!] No GitHub release binary available for '{slug}' on {sys_name}"
        return

    import urllib.request, json
    repo = info["repo"]
    binary = info["binary"]
    tools_dir = TOOLS_DIR
    tools_dir.mkdir(parents=True, exist_ok=True)
    dest = tools_dir / binary

    yield f"[gh] Fetching latest release for {repo} …"
    api_url = f"https://api.github.com/repos/{repo}/releases/latest"
    try:
        req = urllib.request.Request(api_url, headers={"User-Agent": "entr0py"})
        with urllib.request.urlopen(req, timeout=15) as r:
            release = json.loads(r.read())
    except Exception as exc:
        yield f"[!] Could not fetch release info: {exc}"
        return

    assets = release.get("assets", [])
    pattern_lower = asset_pattern.lower()
    match = next((a for a in assets if pattern_lower in a["name"].lower()), None)
    if not match:
        available = ", ".join(a["name"] for a in assets) or "none"
        yield f"[!] No asset matching '{asset_pattern}' in latest release of {repo}"
        yield f"[!] Available assets: {available}"
        return

    asset_name = match["name"]
    download_url = match["browser_download_url"]
    yield f"[gh] Downloading {asset_name} …"

    with tempfile.TemporaryDirectory() as tmp:
        raw = Path(tmp) / asset_name
        try:
            urllib.request.urlretrieve(download_url, raw)
        except Exception as exc:
            yield f"[!] Download failed: {exc}"
            return

        # Extract archives, copy raw binaries directly
        if asset_name.endswith(".tar.gz") or asset_name.endswith(".tgz"):
            import tarfile as _tf
            with _tf.open(raw) as tf:
                # Find the binary inside the archive
                members = [m for m in tf.getmembers()
                           if m.name.endswith(binary) or m.name.endswith(f"/{binary}")]
                if members:
                    members[0].name = binary   # flatten path
                    tf.extract(members[0], tools_dir)
                else:
                    tf.extractall(tools_dir)
        elif asset_name.endswith(".zip"):
            import zipfile as _zf
            with _zf.ZipFile(raw) as zf:
                names = zf.namelist()
                match_name = next(
                    (n for n in names if n.endswith(binary) or n.endswith(f"{binary}.exe")),
                    None,
                )
                if match_name:
                    data = zf.read(match_name)
                    out_name = binary + (".exe" if sys_name == "windows" else "")
                    (tools_dir / out_name).write_bytes(data)
                else:
                    zf.extractall(tools_dir)
        else:
            # Raw binary
            import shutil as _sh
            _sh.copy2(raw, dest)

    # Make executable on Unix
    final = tools_dir / binary
    if final.exists() and sys_name != "windows":
        final.chmod(0o755)

    # Add tools_dir to PATH
    tools_str = str(tools_dir)
    if tools_str not in os.environ.get("PATH", ""):
        os.environ["PATH"] = tools_str + os.pathsep + os.environ.get("PATH", "")

    yield f"[+] {binary} installed to {tools_dir}"


# ---------------------------------------------------------------------------
# System package install
# ---------------------------------------------------------------------------

async def _install_system_pkg(binary: str) -> AsyncIterator[str]:
    mgr = _pkg_manager()
    sys_name = _system()

    if sys_name == "linux":
        pkg = _APT_PKG.get(binary, binary)
        if mgr in ("apt-get", "apt"):
            yield f"[sys] apt-get install -y {pkg}"
            async for line in _run(["sudo", mgr, "install", "-y", pkg]):
                yield line
            return
        if mgr == "pacman":
            yield f"[sys] pacman -S --noconfirm {binary}"
            async for line in _run(["sudo", "pacman", "-S", "--noconfirm", binary]):
                yield line
            return
        if mgr in ("dnf", "yum"):
            yield f"[sys] {mgr} install -y {binary}"
            async for line in _run(["sudo", mgr, "install", "-y", binary]):
                yield line
            return

    if sys_name == "darwin" and shutil.which("brew"):
        pkg = _BREW_PKG.get(binary, binary)
        yield f"[sys] brew install {pkg}"
        async for line in _run(["brew", "install", pkg]):
            yield line
        return

    if sys_name == "windows" and shutil.which("winget"):
        pkg = _WINGET_PKG.get(binary)
        if pkg:
            yield f"[sys] winget install {pkg}"
            async for line in _run(["winget", "install", "--id", pkg, "-e", "--silent"]):
                yield line
            return
        yield f"[!] No winget mapping for '{binary}'. Install it manually."
        return

    yield f"[!] Cannot auto-install '{binary}' — no supported package manager found."


# ---------------------------------------------------------------------------
# Ruby gem install
# ---------------------------------------------------------------------------

async def _install_gem(slug: str) -> AsyncIterator[str]:
    gem_name = _GEM_INSTALL.get(slug)
    if not gem_name:
        return
    if not shutil.which("gem"):
        yield "[ruby] 'gem' not found — installing Ruby first…"
        async for line in _install_system_pkg("gem"):
            yield line
    if shutil.which("gem"):
        yield f"[gem] gem install {gem_name}"
        async for line in _run(["gem", "install", gem_name]):
            yield line
    else:
        yield f"[!] Ruby/gem not available. Install Ruby then run: gem install {gem_name}"


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

async def install_module(module: Module) -> AsyncIterator[str]:
    slug = module.meta.slug
    yield f"[*] Installing {module.meta.name} ({slug}) …"

    if slug in _LINUX_ONLY and _system() == "windows":
        yield f"[!] {module.meta.name} is Linux/macOS only and cannot be installed on Windows."
        return

    # -- pip packages --------------------------------------------------------
    # Use a temp dir without spaces to avoid pip OSError on Windows paths
    # like "C:\Users\asus tuf gaming a15\AppData\Local\Temp\"
    pip_tmp = DATA_DIR / "tmp"
    pip_tmp.mkdir(parents=True, exist_ok=True)
    pip_env = {**os.environ, "TEMP": str(pip_tmp), "TMP": str(pip_tmp), "TMPDIR": str(pip_tmp)}

    for pkg in (_PIP_PACKAGES.get(slug) or module.meta.packages):
        yield f"[pip] Installing {pkg} …"
        async for line in _run(
            [sys.executable, "-m", "pip", "install", "--quiet", pkg],
            env=pip_env,
        ):
            yield line

    # -- Go binary -----------------------------------------------------------
    go_path = _GO_INSTALL.get(slug)
    if go_path:
        if not shutil.which("go"):
            async for line in _install_go():
                yield line
        if shutil.which("go"):
            _ensure_go_in_path()
            yield f"[go] go install {go_path}"
            env = {**os.environ, "GOBIN": str(GO_BIN)}
            async for line in _run(["go", "install", go_path], env=env):
                yield line
            _ensure_go_in_path()
            binary = go_path.split("/")[-1].split("@")[0].rstrip("...")
            if shutil.which(binary):
                yield f"[+] {binary} is now available"
            else:
                yield f"[~] {binary} installed to {GO_BIN} — ensure it is in your PATH"
        else:
            yield "[!] Go installation failed. Install manually from https://go.dev/dl/"

    # -- Rust / cargo --------------------------------------------------------
    crate = _CARGO_INSTALL.get(slug)
    if crate:
        if not shutil.which("cargo"):
            async for line in _install_rust():
                yield line
        if shutil.which("cargo"):
            _ensure_cargo_in_path()
            yield f"[cargo] cargo install {crate}"
            async for line in _run(["cargo", "install", crate]):
                yield line
            _ensure_cargo_in_path()
        else:
            yield "[!] Cargo not available. Install Rust from https://rustup.rs/"

    # -- Ruby gem ------------------------------------------------------------
    if slug in _GEM_INSTALL:
        async for line in _install_gem(slug):
            yield line

    # -- GitHub release binary -----------------------------------------------
    if slug in _GH_RELEASES:
        async for line in _install_gh_release(slug):
            yield line

    # -- Git repos -----------------------------------------------------------
    tools_dir = TOOLS_DIR
    tools_dir.mkdir(parents=True, exist_ok=True)
    repos_to_clone = {**{k: v for k, v in _GIT_REPOS.items() if k == slug},
                      **module.meta.repos}
    for name, url in repos_to_clone.items():
        dest = tools_dir / name
        if dest.exists():
            yield f"[git] Updating {name} …"
            async for line in _run(["git", "-C", str(dest), "pull"]):
                yield line
        else:
            yield f"[git] Cloning {url} …"
            async for line in _run(["git", "clone", "--depth=1", url, str(dest)]):
                yield line
        req = dest / "requirements.txt"
        if req.exists():
            async for line in _run([sys.executable, "-m", "pip", "install", "-r", str(req), "-q"]):
                yield line

    # -- System packages (only for tools with no dedicated installer) ----------
    has_dedicated = (
        bool(_GO_INSTALL.get(slug))
        or bool(_CARGO_INSTALL.get(slug))
        or slug in _GEM_INSTALL
        or slug in _GH_RELEASES
    )

    for tool in module.meta.tools:
        if shutil.which(tool):
            continue
        # If this slug has a Go/cargo/gem/gh installer, only fall back to the
        # system package manager if the tool is explicitly listed in our pkg maps
        # (some tools like amass exist in both apt and go).
        in_pkg_map = (
            tool in _APT_PKG
            or tool in _BREW_PKG
            or tool in _WINGET_PKG
        )
        if has_dedicated and not in_pkg_map:
            # The dedicated installer already ran; no point trying a pkg manager
            # that doesn't know about this tool — skip silently.
            continue
        yield f"[sys] '{tool}' not found — trying system package manager…"
        async for line in _install_system_pkg(tool):
            yield line
        if shutil.which(tool):
            yield f"[+] {tool} is now available"
        else:
            yield f"[~] {tool} may require a new shell/terminal to appear in PATH"

    # -- Custom install steps ------------------------------------------------
    async for line in module.install():
        if not line.startswith("[*] No custom"):
            yield line

    yield f"[+] Done installing {module.meta.name}."
