"""
entr0py.core.wordlists
~~~~~~~~~~~~~~~~~~~~~~
Wordlist registry, downloader, and path resolver.

Wordlists are stored in ~/.entr0py/wordlists/<category>/<filename>.
System paths (/usr/share/wordlists, /usr/share/seclists) are checked
as fallbacks so Kali/Parrot users don't re-download what they already have.
"""
from __future__ import annotations

import gzip
import shutil
import tarfile
from dataclasses import dataclass
from pathlib import Path
from typing import AsyncIterator

import httpx

from entr0py.core.paths import WORDLISTS_DIR

_SYSTEM_PATHS = [
    Path("/usr/share/wordlists"),
    Path("/usr/share/seclists"),
    Path("/usr/share/SecLists"),
    Path("/opt/SecLists"),
]


# ── Wordlist definitions ──────────────────────────────────────────────────────

@dataclass
class Wordlist:
    name:        str
    slug:        str
    category:    str          # passwords | web | dns | fuzzing | usernames
    description: str
    url:         str
    filename:    str          # relative path inside WORDLISTS_DIR
    size_mb:     float = 0.0
    compressed:  str   = ""   # "" | "gz" | "tar.gz"
    system_path: str   = ""   # known relative path under /usr/share/wordlists


REGISTRY: list[Wordlist] = [

    # ── Passwords ─────────────────────────────────────────────────────────────
    Wordlist(
        name="rockyou",
        slug="rockyou",
        category="passwords",
        description="The classic 14M-entry password leak. Required for most password attacks.",
        url="https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Leaked-Databases/rockyou.txt.tar.gz",
        filename="passwords/rockyou.txt",
        size_mb=133.0,
        compressed="tar.gz",
        system_path="rockyou.txt",
    ),
    Wordlist(
        name="darkweb2017 top 10k",
        slug="darkweb10k",
        category="passwords",
        description="10 000 most common passwords from dark web leaks.",
        url="https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/darkweb2017-top10000.txt",
        filename="passwords/darkweb2017-top10000.txt",
        size_mb=0.08,
    ),
    Wordlist(
        name="10k most common",
        slug="common10k",
        category="passwords",
        description="10 000 most commonly used passwords.",
        url="https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10k-most-common.txt",
        filename="passwords/10k-most-common.txt",
        size_mb=0.07,
    ),
    Wordlist(
        name="100k most common",
        slug="common100k",
        category="passwords",
        description="100 000 most commonly used passwords.",
        url="https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/100k-most-common.txt",
        filename="passwords/100k-most-common.txt",
        size_mb=0.8,
    ),

    # ── Web / Directory ───────────────────────────────────────────────────────
    Wordlist(
        name="common (dirb)",
        slug="web-common",
        category="web",
        description="4 600 common web paths. Fast and broad — good first pass.",
        url="https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt",
        filename="web/common.txt",
        size_mb=0.04,
        system_path="dirb/common.txt",
    ),
    Wordlist(
        name="big (dirb)",
        slug="web-big",
        category="web",
        description="20 000 web paths. Thorough directory brute-force.",
        url="https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/big.txt",
        filename="web/big.txt",
        size_mb=0.18,
        system_path="dirb/big.txt",
    ),
    Wordlist(
        name="directory-list-2.3-medium",
        slug="dirbuster-medium",
        category="web",
        description="220 000 directories. The go-to DirBuster medium list.",
        url="https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/directory-list-2.3-medium.txt",
        filename="web/directory-list-2.3-medium.txt",
        size_mb=2.1,
        system_path="dirbuster/directory-list-2.3-medium.txt",
    ),
    Wordlist(
        name="raft-medium-directories",
        slug="raft-medium",
        category="web",
        description="30 000 real-world directory names from RAFT project.",
        url="https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/raft-medium-directories.txt",
        filename="web/raft-medium-directories.txt",
        size_mb=0.25,
    ),
    Wordlist(
        name="raft-large-directories",
        slug="raft-large",
        category="web",
        description="62 000 real-world directory names — the large RAFT list.",
        url="https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/raft-large-directories.txt",
        filename="web/raft-large-directories.txt",
        size_mb=0.56,
    ),
    Wordlist(
        name="api endpoints",
        slug="api-endpoints",
        category="web",
        description="Common REST API endpoint paths for API fuzzing.",
        url="https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/api/api-endpoints.txt",
        filename="web/api-endpoints.txt",
        size_mb=0.02,
    ),

    # ── DNS / Subdomains ──────────────────────────────────────────────────────
    Wordlist(
        name="subdomains top 5 000",
        slug="subdomains-5k",
        category="dns",
        description="Top 5 000 subdomains. Fast subdomain brute-force.",
        url="https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/subdomains-top1million-5000.txt",
        filename="dns/subdomains-top-5000.txt",
        size_mb=0.04,
    ),
    Wordlist(
        name="subdomains top 20 000",
        slug="subdomains-20k",
        category="dns",
        description="Top 20 000 subdomains. Balanced speed vs coverage.",
        url="https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/subdomains-top1million-20000.txt",
        filename="dns/subdomains-top-20000.txt",
        size_mb=0.18,
    ),
    Wordlist(
        name="subdomains top 1M",
        slug="subdomains-1m",
        category="dns",
        description="Full 1 million subdomain list. Comprehensive but slow.",
        url="https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/subdomains-top1million-110000.txt",
        filename="dns/subdomains-top-110000.txt",
        size_mb=0.95,
    ),
    Wordlist(
        name="n0kovo subdomains",
        slug="n0kovo",
        category="dns",
        description="3M unique subdomains compiled from certificate transparency logs.",
        url="https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/n0kovo_subdomains.txt",
        filename="dns/n0kovo-subdomains.txt",
        size_mb=29.0,
    ),

    # ── Fuzzing ───────────────────────────────────────────────────────────────
    Wordlist(
        name="special chars",
        slug="special-chars",
        category="fuzzing",
        description="Special characters for input fuzzing and injection testing.",
        url="https://raw.githubusercontent.com/danielmiessler/SecLists/master/Fuzzing/special-chars.txt",
        filename="fuzzing/special-chars.txt",
        size_mb=0.001,
    ),
    Wordlist(
        name="SQLi generic",
        slug="sqli",
        category="fuzzing",
        description="Generic SQL injection payloads.",
        url="https://raw.githubusercontent.com/danielmiessler/SecLists/master/Fuzzing/SQLi/Generic-SQLi.txt",
        filename="fuzzing/generic-sqli.txt",
        size_mb=0.004,
    ),
    Wordlist(
        name="XSS payloads",
        slug="xss",
        category="fuzzing",
        description="Cross-site scripting payloads for XSS testing.",
        url="https://raw.githubusercontent.com/danielmiessler/SecLists/master/Fuzzing/XSS/XSS-Bypass-Strings-BruteLogic.txt",
        filename="fuzzing/xss-payloads.txt",
        size_mb=0.01,
    ),
    Wordlist(
        name="LFI payloads",
        slug="lfi",
        category="fuzzing",
        description="Local file inclusion path traversal payloads.",
        url="https://raw.githubusercontent.com/danielmiessler/SecLists/master/Fuzzing/LFI/LFI-Jhaddix.txt",
        filename="fuzzing/lfi-payloads.txt",
        size_mb=0.03,
    ),

    # ── Usernames ─────────────────────────────────────────────────────────────
    Wordlist(
        name="top usernames shortlist",
        slug="usernames-short",
        category="usernames",
        description="73 most common usernames. Quick username spray.",
        url="https://raw.githubusercontent.com/danielmiessler/SecLists/master/Usernames/top-usernames-shortlist.txt",
        filename="usernames/top-usernames-shortlist.txt",
        size_mb=0.001,
    ),
    Wordlist(
        name="xato 10M usernames",
        slug="usernames-10m",
        category="usernames",
        description="10 million real-world usernames from xato.net breach data.",
        url="https://raw.githubusercontent.com/danielmiessler/SecLists/master/Usernames/xato-net-10-million-usernames-dup.txt",
        filename="usernames/xato-10m-usernames.txt",
        size_mb=86.0,
    ),
]

# Lookup by slug
_BY_SLUG: dict[str, Wordlist] = {w.slug: w for w in REGISTRY}

# Priority order per use-case: first available (downloaded or on system) wins.
_DEFAULTS: dict[str, list[str]] = {
    "passwords":  ["rockyou", "common100k", "common10k", "darkweb10k"],
    "web":        ["dirbuster-medium", "raft-large", "raft-medium", "web-big", "web-common"],
    "dns":        ["subdomains-20k", "subdomains-5k"],
    "usernames":  ["usernames-short", "usernames-10m"],
    "wifi":       ["rockyou", "common100k", "common10k"],
    "sqli":       ["sqli"],
    "xss":        ["xss"],
    "lfi":        ["lfi"],
}


# ── Path resolution ───────────────────────────────────────────────────────────

def default_path(use_case: str) -> str:
    """
    Return the best available wordlist path for a use-case string.
    Returns "" if nothing is downloaded yet (modules show an empty default).

    use_case values: passwords | web | dns | usernames | wifi | sqli | xss | lfi
    """
    for slug in _DEFAULTS.get(use_case, []):
        p = path(slug)
        if p:
            return str(p)
    return ""


def path(slug: str) -> Path | None:
    """
    Return the local path for a wordlist slug, or None if not downloaded.
    Checks system paths first (Kali/Parrot), then ~/.entr0py/wordlists/.
    """
    wl = _BY_SLUG.get(slug)
    if not wl:
        return None

    # Check system paths
    if wl.system_path:
        for sys_base in _SYSTEM_PATHS:
            candidate = sys_base / wl.system_path
            if candidate.exists():
                return candidate

    # Check local store
    local = WORDLISTS_DIR / wl.filename
    return local if local.exists() else None


def is_downloaded(slug: str) -> bool:
    return path(slug) is not None


def by_category(cat: str) -> list[Wordlist]:
    return [w for w in REGISTRY if w.category == cat]


def categories() -> list[str]:
    seen: list[str] = []
    for w in REGISTRY:
        if w.category not in seen:
            seen.append(w.category)
    return seen


# ── Downloader ────────────────────────────────────────────────────────────────

async def download(slug: str) -> AsyncIterator[str]:
    wl = _BY_SLUG.get(slug)
    if not wl:
        yield f"[!] Unknown wordlist: {slug}"
        return

    dest = WORDLISTS_DIR / wl.filename
    if dest.exists():
        yield f"[+] Already downloaded: {dest}"
        return

    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".tmp")

    yield f"[*] Downloading {wl.name} ({wl.size_mb:.1f} MB)…"
    yield f"[~] {wl.url}"

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=120) as client:
            async with client.stream("GET", wl.url) as resp:
                resp.raise_for_status()
                total   = int(resp.headers.get("content-length", 0))
                received = 0
                with tmp.open("wb") as fh:
                    async for chunk in resp.aiter_bytes(65536):
                        fh.write(chunk)
                        received += len(chunk)
                        if total:
                            pct = received * 100 // total
                            yield f"[~] {pct:>3}%  {received // 1024 // 1024} MB / {total // 1024 // 1024} MB"
    except Exception as exc:
        tmp.unlink(missing_ok=True)
        yield f"[!] Download failed: {exc}"
        return

    # Decompress if needed
    if wl.compressed == "tar.gz":
        yield "[*] Extracting tar.gz…"
        try:
            with tarfile.open(tmp, "r:gz") as tf:
                # Extract the first .txt member
                for member in tf.getmembers():
                    if member.name.endswith(".txt"):
                        member.name = dest.name  # flatten path
                        tf.extract(member, dest.parent)
                        break
        except Exception as exc:
            yield f"[!] Extraction failed: {exc}"
            tmp.unlink(missing_ok=True)
            return
        tmp.unlink(missing_ok=True)

    elif wl.compressed == "gz":
        yield "[*] Decompressing gz…"
        try:
            with gzip.open(tmp, "rb") as gz, dest.open("wb") as out:
                shutil.copyfileobj(gz, out)
        except Exception as exc:
            yield f"[!] Decompression failed: {exc}"
            tmp.unlink(missing_ok=True)
            return
        tmp.unlink(missing_ok=True)

    else:
        tmp.rename(dest)

    yield f"[+] Saved → {dest}"


async def download_all(slugs: list[str] | None = None) -> AsyncIterator[str]:
    targets = [_BY_SLUG[s] for s in slugs if s in _BY_SLUG] if slugs else REGISTRY
    for wl in targets:
        async for line in download(wl.slug):
            yield line
