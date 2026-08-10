"""
entr0py.utils.reporter
~~~~~~~~~~~~~~~~~~~~~~
Generate JSON and HTML reports from scan output files.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def generate_json(
    module_slug: str,
    opts: dict,
    output_lines: list[str],
    output_path: Path,
) -> Path:
    report = {
        "framework":  "entr0py",
        "module":     module_slug,
        "opts":       opts,
        "generated":  _now(),
        "line_count": len(output_lines),
        "output":     output_lines,
    }
    report_path = output_path.with_suffix(".report.json")
    report_path.write_text(json.dumps(report, indent=2))
    return report_path


_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>entr0py — {module} report</title>
  <style>
    body   {{ background:#0a0a0f; color:#c8c8d4; font-family:monospace; padding:2em; }}
    h1     {{ color:#00ff9f; }}
    h2     {{ color:#4444aa; border-bottom:1px solid #1a1a2e; padding-bottom:.3em; }}
    table  {{ border-collapse:collapse; margin-bottom:1em; }}
    td,th  {{ padding:.3em .8em; border:1px solid #1a1a3e; text-align:left; }}
    th     {{ background:#0d0d1a; color:#00ff9f; }}
    pre    {{ background:#080810; padding:1em; border:1px solid #1a1a3e;
              overflow-x:auto; color:#aaffaa; font-size:.85em; }}
    .dim   {{ color:#4a4a6a; }}
  </style>
</head>
<body>
  <h1>entr0py — {module} report</h1>
  <p class="dim">Generated: {generated}</p>

  <h2>Options</h2>
  <table>
    <tr><th>Option</th><th>Value</th></tr>
    {opts_rows}
  </table>

  <h2>Output ({line_count} lines)</h2>
  <pre>{output}</pre>
</body>
</html>
"""


def generate_html(
    module_slug: str,
    opts: dict,
    output_lines: list[str],
    output_path: Path,
) -> Path:
    opts_rows = "\n    ".join(
        f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in opts.items()
    )
    html = _HTML_TEMPLATE.format(
        module=module_slug,
        generated=_now(),
        opts_rows=opts_rows,
        line_count=len(output_lines),
        output="\n".join(output_lines).replace("<", "&lt;").replace(">", "&gt;"),
    )
    report_path = output_path.with_suffix(".report.html")
    report_path.write_text(html, encoding="utf-8")
    return report_path


def report_from_file(output_path: Path, fmt: str = "json") -> Path:
    """Re-generate a report from an existing output file."""
    lines = output_path.read_text(encoding="utf-8", errors="replace").splitlines()
    slug  = output_path.stem.split("_")[0]
    if fmt == "html":
        return generate_html(slug, {}, lines, output_path)
    return generate_json(slug, {}, lines, output_path)


# ---------------------------------------------------------------------------
# Session reports — aggregate every run in a session into one deliverable,
# extracting structured findings/artifacts via each module's parse().
# ---------------------------------------------------------------------------

def _esc(s: object) -> str:
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


async def _collect_session(session_id: int) -> tuple[dict, list[str], list[dict]]:
    """Read a session + its runs, attaching parsed findings to each run."""
    import entr0py.modules  # noqa: F401 — register modules so parse() is available
    from entr0py.core import session as session_mod
    from entr0py.core.registry import get_registry

    sess = await session_mod.get_session(session_id)
    if sess is None:
        raise ValueError(f"No session #{session_id}")
    runs = list(reversed(await session_mod.list_runs(session_id)))  # chronological
    registry = get_registry()

    entries: list[dict] = []
    for r in runs:
        opts = json.loads(r["opts_json"] or "{}")
        target = (opts.get("target") or opts.get("domain") or opts.get("url")
                  or opts.get("apk") or opts.get("host") or "")
        lines: list[str] = []
        op = r["output_path"]
        if op and Path(op).exists():
            lines = Path(op).read_text(encoding="utf-8", errors="replace").splitlines()
        module = registry.get(r["module_slug"])
        findings = module.parse(lines) if module else []
        entries.append({"run": r, "target": target, "lines": lines, "findings": findings})

    scope = json.loads(sess["scope_json"] or "[]")
    return sess, scope, entries


def _session_md(sess: dict, scope: list[str], entries: list[dict]) -> str:
    out = [
        f"# entr0py session report — {sess['name']} (#{sess['id']})",
        "",
        f"- **Created:** {sess['created_at']}",
        f"- **Scope:** {', '.join(scope) or '_none_'}",
        f"- **Runs:** {len(entries)}",
        f"- **Generated:** {_now()}",
        "",
        "## Summary",
        "",
        "| Run | Module | Target | Status | Findings |",
        "|----:|--------|--------|--------|---------:|",
    ]
    for e in entries:
        r = e["run"]
        out.append(f"| {r['id']} | {r['module_slug']} | {e['target'] or '—'} "
                   f"| {r['status']} | {len(e['findings'])} |")
    out.append("")
    for e in entries:
        r = e["run"]
        out += [
            f"## {r['module_slug']} — run #{r['id']}",
            "",
            f"Target: `{e['target'] or '—'}` · Status: **{r['status']}** · "
            f"{r['started_at']} → {r['finished_at'] or '—'}",
            "",
        ]
        if e["findings"]:
            out.append(f"**Findings / artifacts ({len(e['findings'])}):**")
            out.append("")
            out += [f"- `{f}`" for f in e["findings"][:200]]
            if len(e["findings"]) > 200:
                out.append(f"- … and {len(e['findings']) - 200} more")
        else:
            out.append("_No structured findings extracted._")
        out += ["", "<details><summary>Raw output</summary>", "", "```"]
        out += e["lines"][:500]
        if len(e["lines"]) > 500:
            out.append(f"... ({len(e['lines']) - 500} more lines truncated)")
        out += ["```", "", "</details>", ""]
    return "\n".join(out)


_SESSION_HTML = """\
<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<title>entr0py — session #{sid} report</title><style>
 body{{background:#0a0a0f;color:#c8c8d4;font-family:monospace;padding:2em;max-width:1100px;margin:auto}}
 h1{{color:#00ff9f}} h2{{color:#7a7aff;border-bottom:1px solid #1a1a2e;padding-bottom:.3em;margin-top:2em}}
 table{{border-collapse:collapse;margin:1em 0;width:100%}} td,th{{padding:.35em .8em;border:1px solid #1a1a3e;text-align:left}}
 th{{background:#0d0d1a;color:#00ff9f}} code{{color:#aaffaa}} .dim{{color:#5a5a7a}}
 pre{{background:#080810;padding:1em;border:1px solid #1a1a3e;overflow-x:auto;color:#9f9;font-size:.82em}}
 ul{{line-height:1.6}} summary{{cursor:pointer;color:#7a7aff}}</style></head><body>
<h1>entr0py — {name} <span class="dim">(session #{sid})</span></h1>
<p class="dim">Created {created} · Scope: {scope} · {nruns} run(s) · generated {generated}</p>
<h2>Summary</h2><table><tr><th>Run</th><th>Module</th><th>Target</th><th>Status</th><th>Findings</th></tr>
{rows}</table>
{sections}
</body></html>
"""


def _session_html(sess: dict, scope: list[str], entries: list[dict]) -> str:
    rows = "\n".join(
        f"<tr><td>{e['run']['id']}</td><td>{_esc(e['run']['module_slug'])}</td>"
        f"<td>{_esc(e['target'] or '—')}</td><td>{_esc(e['run']['status'])}</td>"
        f"<td>{len(e['findings'])}</td></tr>"
        for e in entries
    )
    sections = []
    for e in entries:
        r = e["run"]
        items = "".join(f"<li><code>{_esc(f)}</code></li>" for f in e["findings"][:200]) \
            or "<li class='dim'>No structured findings extracted.</li>"
        raw = _esc("\n".join(e["lines"][:500]))
        sections.append(
            f"<h2>{_esc(r['module_slug'])} <span class='dim'>run #{r['id']}</span></h2>"
            f"<p class='dim'>Target: {_esc(e['target'] or '—')} · {_esc(r['status'])} · "
            f"{_esc(r['started_at'])}</p><ul>{items}</ul>"
            f"<details><summary>Raw output</summary><pre>{raw}</pre></details>"
        )
    return _SESSION_HTML.format(
        sid=sess["id"], name=_esc(sess["name"]), created=_esc(sess["created_at"]),
        scope=_esc(", ".join(scope) or "none"), nruns=len(entries), generated=_now(),
        rows=rows, sections="\n".join(sections),
    )


async def build_session_report(session_id: int, fmt: str = "md") -> Path:
    """Aggregate a whole session into one Markdown / HTML / JSON deliverable."""
    from entr0py.core.paths import DATA_DIR

    sess, scope, entries = await _collect_session(session_id)
    if fmt == "html":
        content, ext = _session_html(sess, scope, entries), ".html"
    elif fmt == "json":
        content = json.dumps({
            "session": sess, "scope": scope,
            "runs": [{"run": e["run"], "target": e["target"],
                      "findings": e["findings"]} for e in entries],
        }, indent=2)
        ext = ".json"
    else:
        content, ext = _session_md(sess, scope, entries), ".md"

    report_dir = DATA_DIR / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    out = report_dir / f"session_{session_id}{ext}"
    out.write_text(content, encoding="utf-8")
    return out
