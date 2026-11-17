#!/usr/bin/env python3
"""Build docs/index.html, a standalone demo of every template.

Each template is embedded in an iframe (srcdoc) with two stand-ins for the
Muse environment:

  - an in-memory window.hatchWidget bridge, so interactive components work
    in a plain browser (state resets when the page reloads);
  - the --hatch-widget-* theme variables, defined for light and dark
    color schemes, so components render with the same colors they get
    inside Muse. Without these, every themed element falls back to
    transparent and the demo looks broken.

Iframes report their content height to the parent page, which resizes
them, so small components do not sit in a tall empty frame.

Run after changing any template:

    python3 tools/build-demo.py
"""

from __future__ import annotations

import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _harness import THEME, SHIM  # noqa: E402,F401  (single source in _harness.py)

ROOT = Path(__file__).resolve().parent.parent

DESCRIPTIONS = {
    "badge": "A single status word that matters, filled or outlined.",
    "button-row": "Shared button styling and interaction states.",
    "calculator": "Several inputs, premises up front, one hero result.",
    "card": "One self-contained point: a summary, a result, a notice.",
    "chip-row": "Attributes at a glance. Not for choices.",
    "comparison-grid": "Two to four options side by side.",
    "conditional-comparison": "A fixed table whose recommendation follows the reader's condition.",
    "editable-checklist": "Items the reader ticks off; state the agent can read back.",
    "input-form": "Up to five short fields, recorded as widget state.",
    "interactive-chart": "One chart, switchable metric, data embedded.",
    "progress-bar": "Segmented progress, always with counts in words.",
    "segmented-control": "Two to five discrete options with explanations.",
    "slider-linked-value": "Sweep one quantity while a derived total follows.",
    "tabs": "Up to four sections, all content shipped in the fragment.",
    "timeline": "Ordered steps or events with times.",
}

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>muse-widgets — interactive chat widgets for Muse</title>
<style>
  :root { color-scheme: light dark; }
  body { font-family: system-ui, -apple-system, "Segoe UI", sans-serif; margin: 0; padding: 32px 16px 72px; line-height: 1.6; }
  main { max-width: 46rem; margin: 0 auto; }
  h1 { font-size: 26px; margin: 0 0 6px; }
  h2 { font-size: 17px; margin: 0 0 2px; }
  p.lead { opacity: 0.75; margin: 0 0 10px; }
  p.note { opacity: 0.65; font-size: 13px; margin: 2px 0 10px; }
  nav { display: flex; flex-wrap: wrap; gap: 6px 14px; font-size: 13px; margin: 18px 0 6px; }
  section { border-top: 1px solid rgba(128, 128, 128, 0.35); padding: 26px 0 6px; margin-top: 26px; }
  iframe { width: 100%; border: 1px solid rgba(128, 128, 128, 0.45); border-radius: 12px; background: transparent; display: block; }
  code { font-family: ui-monospace, monospace; font-size: 0.92em; }
</style>
</head>
<body>
<main>
  <h1>muse-widgets demo</h1>
  <p class="lead">Every component in the catalog, live. The interactive ones run against an in-memory stand-in for the Muse state bridge, so state resets when this page reloads. Inside Muse, the same fragments persist their state with the conversation.</p>
  <p class="note">Unofficial project. See the <a href="https://github.com/Hyd3-14/muse-widgets">repository</a> for the catalog, the agent skill, and the validator.</p>
  <nav>
__NAV__
  </nav>
__SECTIONS__
</main>
<script>
  window.addEventListener('message', function (e) {
    if (!e.data || typeof e.data.mwHeight !== 'number') return;
    var frames = document.querySelectorAll('iframe');
    for (var i = 0; i < frames.length; i++) {
      if (frames[i].contentWindow === e.source) {
        frames[i].style.height = e.data.mwHeight + 'px';
      }
    }
  });
</script>
</body>
</html>
"""


HEIGHT_REPORTER = """
<script>
  (function () {
    function report() {
      var h = document.documentElement.scrollHeight;
      parent.postMessage({ mwHeight: h }, '*');
    }
    window.addEventListener('load', report);
    new ResizeObserver(report).observe(document.body);
  })();
</script>
"""


def frame_doc(template: Path) -> str:
    from _harness import frame_doc as _frame_doc
    return _frame_doc(template.read_text(encoding="utf-8"), HEIGHT_REPORTER)


def section(template: Path) -> str:
    doc = frame_doc(template)
    desc = DESCRIPTIONS.get(template.stem, "")
    return (
        f'  <section id="{html.escape(template.stem)}">\n'
        f'    <h2>{html.escape(template.stem)}</h2>\n'
        f'    <p class="note">{html.escape(desc)} '
        f'<code>templates/{html.escape(template.name)}</code></p>\n'
        f'    <iframe title="{html.escape(template.stem)}" height="160" '
        f'srcdoc="{html.escape(doc, quote=True)}"></iframe>\n'
        f'  </section>\n'
    )


def main() -> None:
    templates = sorted((ROOT / "templates").glob("*.html"))
    nav = "\n".join(
        f'    <a href="#{html.escape(t.stem)}">{html.escape(t.stem)}</a>'
        for t in templates
    )
    out = PAGE.replace("__NAV__", nav).replace("__SECTIONS__", "\n".join(section(t) for t in templates))
    target = ROOT / "docs" / "index.html"
    target.write_text(out, encoding="utf-8")
    print(f"wrote {target} with {len(templates)} components")


if __name__ == "__main__":
    main()
