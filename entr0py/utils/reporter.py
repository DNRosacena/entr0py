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
