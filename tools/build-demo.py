#!/usr/bin/env python3
"""Build docs/index.html, a standalone demo of every template.

Each template is embedded in an iframe (srcdoc) with a small in-memory
stand-in for window.hatchWidget, so the interactive components work in a
plain browser. Run after changing any template:

    python3 tools/build-demo.py
"""

from __future__ import annotations

import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SHIM = """
<script>
  window.hatchWidget = (function () {
    var state = null;
    return {
      getState: function (defaults) {
        if (state === null) state = JSON.parse(JSON.stringify(defaults));
        return state;
      },
      setState: function (next) {
        state = next;
        window.dispatchEvent(new CustomEvent('hatch-widget-state', { detail: { state: state } }));
      }
    };
  })();
</script>
"""

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>muse-widgets — interactive chat widgets for Muse</title>
<style>
  :root {{ color-scheme: light dark; }}
  body {{ font-family: system-ui, -apple-system, "Segoe UI", sans-serif; margin: 0; padding: 24px 16px 64px; line-height: 1.6; }}
  main {{ max-width: 44rem; margin: 0 auto; }}
  h1 {{ font-size: 24px; margin: 0 0 4px; }}
  h2 {{ font-size: 17px; margin: 40px 0 4px; }}
  p.lead {{ color: #666; margin: 0 0 8px; }}
  p.note {{ color: #666; font-size: 13px; margin: 4px 0 8px; }}
  iframe {{ width: 100%; border: 1px solid #ccc; border-radius: 12px; background: transparent; }}
  code {{ font-family: ui-monospace, monospace; font-size: 0.92em; }}
</style>
</head>
<body>
<main>
  <h1>muse-widgets demo</h1>
  <p class="lead">Every component in the catalog, live. The interactive ones run against an in-memory stand-in for the Muse state bridge, so state resets when this page reloads. Inside Muse, the same fragments persist their state with the conversation.</p>
  <p class="note">Unofficial project. See the <a href="https://github.com/Hyd3-14/muse-widgets">repository</a> for the catalog, the agent skill, and the validator.</p>
{sections}
</main>
</body>
</html>
"""


def section(template: Path) -> str:
    fragment = template.read_text(encoding="utf-8")
    doc = ("<!DOCTYPE html><html><head><meta charset='utf-8'>"
           "<style>:root{color-scheme:light dark}body{margin:0}</style>"
           + SHIM + "</head><body>" + fragment + "</body></html>")
    return (
        f'  <h2>{html.escape(template.stem)}</h2>\n'
        f'  <p class="note"><code>templates/{html.escape(template.name)}</code></p>\n'
        f'  <iframe title="{html.escape(template.stem)}" height="340" '
        f'srcdoc="{html.escape(doc, quote=True)}"></iframe>\n'
    )


def main() -> None:
    templates = sorted((ROOT / "templates").glob("*.html"))
    out = PAGE.format(sections="\n".join(section(t) for t in templates))
    target = ROOT / "docs" / "index.html"
    target.write_text(out, encoding="utf-8")
    print(f"wrote {target} with {len(templates)} components")


if __name__ == "__main__":
    main()
