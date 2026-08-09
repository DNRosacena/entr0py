# ─────────────────────────────────────────────────────────────────────────────
#  entr0py — Containerized Pentesting Framework
#  Base: Kali Linux Rolling (pre-ships ~90% of required tools via apt)
# ─────────────────────────────────────────────────────────────────────────────
FROM kalilinux/kali-rolling

# Suppress interactive prompts from apt
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# ── entr0py data root — paths.py checks ENTR0PY_DATA_DIR first ───────────────
# On Linux it would default to ~/.entr0py, but we pin it to /opt/entr0py/data
# so volumes, reports, and tool binaries all land in a predictable place.
ENV ENTR0PY_DATA_DIR=/opt/entr0py/data

# ── Go — install to DATA_DIR/go so setup_env() finds the bin dir ─────────────
ENV GOPATH=/opt/entr0py/data/go
ENV GOBIN=/opt/entr0py/data/go/bin
ENV PATH=$PATH:/usr/local/go/bin:/opt/entr0py/data/go/bin

# ── Rust — install to DATA_DIR/cargo so setup_env() finds the bin dir ────────
ENV CARGO_HOME=/opt/entr0py/data/cargo
ENV PATH=$PATH:/opt/entr0py/data/cargo/bin

# ─────────────────────────────────────────────────────────────────────────────
#  STAGE 1 — System packages
#  Kali Rolling ships most pentesting tools — we install them all up front
#  so the runtime installer finds them via shutil.which() and skips re-install.
# ─────────────────────────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Python runtime
    python3 python3-pip python3-dev \
    # Core utilities
    git curl wget \
    # Network tools
    nmap masscan netcat-traditional netdiscover \
    # Password tools
    hydra john hashcat crunch \
    # Web tools
    sqlmap nikto \
    # Wireless (Linux-only — baked in but need hw passthrough at runtime)
    aircrack-ng hcxdumptool hcxtools kismet wifite \
    # Forensics
    binwalk foremost steghide libimage-exiftool-perl \
    # Exploitation / Post-exploit
    metasploit-framework exploitdb set \
    # Language runtimes (for gem / cargo installs)
    ruby ruby-dev \
    golang-go \
    cargo \
    # Build deps needed by some pip packages
    libssl-dev libffi-dev build-essential \
    && rm -rf /var/lib/apt/lists/*

# ─────────────────────────────────────────────────────────────────────────────
#  retry helper — re-attempts a flaky, network-bound command up to 5 times.
#  The build target is often an unstable connection; a transient "connection
#  reset by peer" from a package proxy should retry, not abort the whole build.
# ─────────────────────────────────────────────────────────────────────────────
RUN printf '#!/bin/sh\nn=0; until [ "$n" -ge 5 ]; do "$@" && exit 0; n=$((n+1)); echo "[retry] attempt $n/5 failed: $*"; sleep 10; done; echo "[retry] gave up after 5 attempts: $*" >&2; exit 1\n' \
      > /usr/local/bin/retry && chmod +x /usr/local/bin/retry

# ─────────────────────────────────────────────────────────────────────────────
#  STAGE 2 — Go binaries
#  ProjectDiscovery suite + standalone Go tools.
#  Split into separate RUN layers so each compiled tool caches independently —
#  a failure in one no longer discards the (slow) compiles that already succeeded.
#  Each is wrapped in `retry` to survive transient network resets mid-download.
# ─────────────────────────────────────────────────────────────────────────────
RUN retry go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
RUN retry go install github.com/projectdiscovery/httpx/cmd/httpx@latest
RUN retry go install github.com/projectdiscovery/dnsx/cmd/dnsx@latest
RUN retry go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
RUN retry go install github.com/projectdiscovery/katana/cmd/katana@latest
RUN retry go install github.com/owasp-amass/amass/v4/...@latest
RUN retry go install github.com/ffuf/ffuf/v2@latest
RUN retry go install github.com/hahwul/dalfox/v2@latest
# traitor's main package is in cmd/traitor, not the module root
RUN retry go install github.com/liamg/traitor/cmd/traitor@latest
# bettercap is a cgo build — it needs pkg-config and the libpcap / libusb /
# libnetfilter-queue development headers. Kept in its own small apt layer here
# (rather than in the big Stage 1 install) so the already-compiled Go tools above
# stay cached instead of rebuilding.
RUN retry sh -c 'apt-get update && apt-get install -y --no-install-recommends \
      pkg-config libpcap-dev libusb-1.0-0-dev libnetfilter-queue-dev \
    && rm -rf /var/lib/apt/lists/*'
RUN retry go install github.com/bettercap/bettercap@latest
RUN retry go install github.com/gophish/gophish@latest

# ─────────────────────────────────────────────────────────────────────────────
#  STAGE 3 — Rust (RustScan)
# ─────────────────────────────────────────────────────────────────────────────
RUN retry cargo install rustscan

# ─────────────────────────────────────────────────────────────────────────────
#  STAGE 4 — Kali apt tools that are NOT pip/gem packages
#  CeWL + WhatWeb are Ruby tools not on rubygems; theHarvester on PyPI is only a
#  placeholder stub (v0.0.1) — the real tool ships as the Kali apt package; stegseek
#  is a standalone forensics tool (apt, distinct from steghide). Install via apt
#  (they pull their own gem/python deps).
# ─────────────────────────────────────────────────────────────────────────────
RUN retry sh -c 'apt-get update && apt-get install -y --no-install-recommends \
      cewl whatweb theharvester stegseek \
    && rm -rf /var/lib/apt/lists/*'

# ─────────────────────────────────────────────────────────────────────────────
#  STAGE 5 — Python packages (runtime tool deps)
# ─────────────────────────────────────────────────────────────────────────────
RUN retry pip install --break-system-packages \
    sherlock-project \
    maigret \
    holehe \
    s3scanner \
    sqlmap \
    arjun \
    wafw00f \
    volatility3
# (wifite is installed via apt in Stage 1 — there is no `wifite2` package on PyPI;
#  theHarvester is installed via apt in Stage 4 — its PyPI entry is only a stub)

# ─────────────────────────────────────────────────────────────────────────────
#  STAGE 6 — Git-cloned + downloaded tools
#  These MUST live under TOOLS_DIR (= $ENTR0PY_DATA_DIR/tools = /opt/entr0py/data/
#  tools), because the cupp/corsy/pspy/linpeas modules resolve their script/binary
#  relative to TOOLS_DIR. The old /opt/tools location was invisible to them, so the
#  modules reported "installed" (empty tool-list) yet failed at run time.
#  (Dropped the XSStrike clone — no module uses it — and the exploit-database clone
#  — searchsploit runs from the apt `exploitdb` package, the ~1 GB clone was dead.)
# ─────────────────────────────────────────────────────────────────────────────
RUN mkdir -p /opt/entr0py/data/tools && \
    retry git clone --depth=1 https://github.com/s0md3v/Corsy /opt/entr0py/data/tools/Corsy && \
    retry git clone --depth=1 https://github.com/Mebus/cupp   /opt/entr0py/data/tools/cupp

# Install requirements for each cloned repo if present
RUN for dir in /opt/entr0py/data/tools/*/; do \
      [ -f "$dir/requirements.txt" ] && \
      retry pip install --break-system-packages -r "$dir/requirements.txt" -q || true; \
    done

# pspy + linpeas — the modules invoke these from TOOLS_DIR but only fetch them on an
# explicit `entr0py install`. Bake them in at the exact paths/names the modules use
# so they work out of the box (URLs match the modules' own install() definitions).
RUN retry curl -fsSL -o /opt/entr0py/data/tools/pspy64 \
      https://github.com/DominicBreuker/pspy/releases/latest/download/pspy64 && \
    chmod +x /opt/entr0py/data/tools/pspy64
RUN retry curl -fsSL -o /opt/entr0py/data/tools/linpeas.sh \
      https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh && \
    chmod +x /opt/entr0py/data/tools/linpeas.sh

# ─────────────────────────────────────────────────────────────────────────────
#  STAGE 6b — Additional Go tools (evilginx2, phoneinfoga)
#  Placed here rather than in Stage 2 so adding them doesn't invalidate the cache
#  for rustscan / apt / pip / git above.
# ─────────────────────────────────────────────────────────────────────────────
# evilginx2's go.mod carries `replace` directives, so `go install` from outside the
# module is refused — clone and `go build` from *inside* the module (where replaces
# are honored). Binary is emitted as `evilginx2` onto GOBIN (already on PATH); the
# clone keeps its phishlets/ + redirectors/ alongside for runtime `-p`.
RUN retry git clone --depth=1 https://github.com/kgretzky/evilginx2 /opt/tools/evilginx && \
    cd /opt/tools/evilginx && \
    retry go build -o /opt/entr0py/data/go/bin/evilginx2 .
# phoneinfoga can't be `go install`ed — web/client.go embeds `client/dist/*` (a
# separately-built frontend not shipped in the Go module zip), so the build fails on
# a missing embed pattern. Upstream's supported path is the prebuilt release binary
# (web assets already baked in). Fetch the latest Linux x86_64 asset onto PATH.
RUN retry sh -c 'set -eu; \
  url=$(curl -fsSL https://api.github.com/repos/sundowndev/phoneinfoga/releases/latest \
        | grep -oiP "\"browser_download_url\":\s*\"\K[^\"]*linux[^\"]*(x86_64|amd64)[^\"]*\.tar\.gz" \
        | head -1); \
  test -n "$url"; \
  curl -fsSL "$url" -o /tmp/pi.tgz; \
  mkdir -p /tmp/pi && tar -xzf /tmp/pi.tgz -C /tmp/pi; \
  install -m0755 "$(find /tmp/pi -type f -name phoneinfoga)" /opt/entr0py/data/go/bin/phoneinfoga; \
  rm -rf /tmp/pi /tmp/pi.tgz'

# gophish — the `go install` binary (in Stage 2) can't run standalone: it reads
# ./VERSION, config.json, static/ and templates/ from its working directory and
# aborts without them. Install the official release layout and put a PATH wrapper on
# /usr/local/bin (which precedes GOBIN) that runs gophish from that directory.
RUN retry sh -c 'command -v unzip >/dev/null || { apt-get update && apt-get install -y --no-install-recommends unzip && rm -rf /var/lib/apt/lists/*; }'
RUN mkdir -p /opt/gophish && cd /opt/gophish && \
    retry sh -c 'url=$(curl -fsSL https://api.github.com/repos/gophish/gophish/releases/latest \
        | grep -oiP "\"browser_download_url\":\s*\"\K[^\"]*inux[^\"]*64[^\"]*\.zip" | head -1); \
      test -n "$url"; curl -fsSL "$url" -o g.zip' && \
    unzip -q g.zip && rm g.zip && chmod +x gophish && \
    printf '#!/bin/sh\ncd /opt/gophish && exec ./gophish "$@"\n' > /usr/local/bin/gophish && \
    chmod +x /usr/local/bin/gophish

# ─────────────────────────────────────────────────────────────────────────────
#  STAGE 7 — entr0py itself
# ─────────────────────────────────────────────────────────────────────────────
WORKDIR /opt/entr0py
COPY . .

# Fix hardcoded Windows paths in config
RUN sed -i 's|D:/entr0py|/opt/entr0py/data|g' config/default.toml

# Install entr0py Python dependencies
RUN retry pip install --break-system-packages -e .

# Create all dirs that setup_env() checks for existence before adding to PATH.
# If these don't exist at startup, setup_env() silently skips them.
RUN mkdir -p \
    /opt/entr0py/data/reports \
    /opt/entr0py/data/tmp \
    /opt/entr0py/data/go/bin \
    /opt/entr0py/data/cargo/bin \
    /opt/entr0py/data/tools \
    /opt/tools

# ─────────────────────────────────────────────────────────────────────────────
#  ENTRYPOINT
# ─────────────────────────────────────────────────────────────────────────────
ENTRYPOINT ["python3", "-m", "entr0py"]
