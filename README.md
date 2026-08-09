# entr0py

**A modular, containerized penetration-testing framework.**

entr0py is a meta-framework: instead of reimplementing security tools, it orchestrates
**54 battle-tested open-source tools** behind one consistent interface — an interactive TUI
and a scriptable CLI — all packaged into a single reproducible Docker image (Kali-based).
Point it at a target, pick a tool, get streamed output. Reconnaissance through
post-exploitation, plus Android app analysis.

Inspired by [fsociety](https://github.com/Manisso/fsociety), rebuilt around a clean module
API, session/scope management, and a portable container.

---

## ⚠️ Authorized use only

entr0py is for **authorized security testing and education only**. Use it exclusively against
systems, applications, and devices that **you own or have explicit written permission to test**.

Unauthorized scanning, exploitation, credential attacks, or payload deployment against systems
you do not own is **illegal** in most jurisdictions. The payload-generation and exploitation
modules (`metasploit`, `android_payload`, `drozer`, etc.) can cause real harm — you are solely
responsible for how you use them. The authors assume no liability for misuse.

---

## Quick start (Docker)

```bash
git clone git@github.com:DNRosacena/entr0py.git
cd entr0py
docker compose build          # builds the Kali-based image (first build is large)
docker compose run --rm entr0py          # launch the interactive TUI
```

Headless / scripted:

```bash
docker compose run --rm entr0py list                       # list all modules
docker compose run --rm entr0py search nmap                # search modules
docker compose run --rm entr0py run subfinder domain=example.com
docker compose run --rm entr0py run nuclei target=https://example.com severity=high,critical
```

> The compose service runs with `network_mode: host` and the `NET_ADMIN` / `NET_RAW`
> capabilities so raw-socket and wireless tools (nmap, masscan, bettercap, aircrack, …)
> work. Reports persist to `./data/reports/` on the host.

## Toolbox — 54 modules across 11 categories

| Category | # | Tools |
|---|---|---|
| Reconnaissance | 6 | subfinder, amass, httpx, dnsx, katana, theHarvester |
| OSINT | 5 | sherlock, maigret, holehe, s3scanner, phoneinfoga |
| Network | 5 | nmap, masscan, rustscan, netdiscover, bettercap |
| Web Applications | 9 | nuclei, sqlmap, nikto, ffuf, dalfox, arjun, wafw00f, whatweb, corsy |
| Passwords & Hashes | 6 | hashcat, john, hydra, crunch, cewl, cupp |
| Exploitation | 2 | metasploit, searchsploit |
| Post-Exploitation | 3 | linpeas, pspy, traitor |
| Wireless | 4 | aircrack-ng, wifite, hcxdumptool, kismet |
| Forensics | 5 | binwalk, foremost, exiftool, stegseek, volatility3 |
| Social Engineering | 3 | setoolkit, gophish, evilginx2 |
| Mobile (Android) | 6 | apktool, jadx, dex2jar, apkleaks, android_payload, drozer |

## CLI reference

```
entr0py                          Launch the interactive TUI
entr0py list [--category X]      List modules (optionally by category)
entr0py search <query>           Search modules by name/tag/description
entr0py run <slug> [k=v …]       Run a module headlessly (key=value options)
entr0py install <slug>           Install a module's dependencies (non-Docker hosts)
entr0py scope add <target>       Add a target to the active scope
entr0py session new <name>       Create a scan session
entr0py wordlists                Manage/download wordlists
entr0py report <file> [--fmt]    Generate a report from saved output
```

## Architecture

- **`core/`** — module base classes, registry, executor, scope/session engine, installer, paths.
- **`modules/<category>/`** — one file per tool; each is a `Module` subclass declaring its
  metadata (required binaries, packages) and an async `run()` that streams output.
- **`ui/`** — the Rich/pyfiglet terminal menu. **`__main__.py`** — the Typer CLI.
- **`Dockerfile`** — Kali base; installs the toolchain (apt / Go / Rust / Ruby / pip / release
  binaries) with each step in its own cached layer and a retry wrapper for flaky networks.

Adding a tool = drop a new `Module` subclass into the right category package and register it.

## Local install (without Docker)

Requires Python 3.11+. Individual tools are installed on demand:

```bash
pip install -e .
entr0py install <slug>     # fetches that tool via apt/go/cargo/gem/pip/release as appropriate
```

The container is the supported path — it guarantees every tool is present and pinned.

## Notes

- **mimikatz is intentionally excluded** — it's a native Windows tool with no Linux build and
  can't run in this container. For Windows engagements, run it on a Windows host or load it
  remotely via Metasploit.
- Android **dynamic** instrumentation (frida/objection) is not bundled — it needs a device or
  emulator. The Android modules here are static analysis + payload generation + `drozer`
  (which connects to a device agent over `adb`).

## License

MIT — see `pyproject.toml`. The bundled third-party tools retain their own licenses.
