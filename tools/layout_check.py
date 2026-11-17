#!/usr/bin/env python3
"""Render every template in real browser engines and fail on layout breakage.

The static validator (validate-widget.py) catches broken markup and risky
CSS patterns, but some breakage only exists after layout: an iOS date
input whose intrinsic minimum width exceeds its card, a flex row that
pushes past the viewport, a grid cell that will not shrink. Those need a
real engine. This check renders each fragment in the demo harness
(theme variables + state bridge stand-ins) at phone widths and fails if
any element extends past the viewport or past its own container
horizontally, in the initial state
and after clicking every button (tab and segment switches change layout).

Requires Playwright and its browsers:

    pip install playwright
    playwright install --with-deps chromium webkit

WebKit matters: Muse's primary client is an iOS app, and WebKit is the
closest engine to it. Chromium alone would miss WebKit-only sizing
behavior such as native date controls.

Usage:
    python3 tools/layout_check.py [--engines chromium,webkit] [paths...]

With no paths it checks templates/ and examples/. Exit code is 1 when
any file breaks in any engine at any width.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _harness import frame_doc  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
WIDTHS = (375, 320)

MEASURE = """() => {
  const vw = document.documentElement.clientWidth;
  const bad = [];
  const clips = (el) => {
    const s = getComputedStyle(el).overflowX;
    return s === 'hidden' || s === 'clip' || s === 'auto' || s === 'scroll';
  };
  document.querySelectorAll('*').forEach((el) => {
    const r = el.getBoundingClientRect();
    if (!r.width) return;
    let why = '';
    if (r.right > vw + 1 || r.left < -1) {
      why = 'past viewport';
    } else if (el.parentElement && !clips(el.parentElement)) {
      const pr = el.parentElement.getBoundingClientRect();
      if (r.right > pr.right + 1 || r.left < pr.left - 1) why = 'past parent';
    }
    if (why) {
      const cls = typeof el.className === 'string' && el.className
        ? '.' + el.className.split(' ')[0] : '';
      bad.push(el.tagName.toLowerCase() + cls + ' ' + why + ' right=' + r.right.toFixed(1));
    }
  });
  return { vw: vw, scrollWidth: document.documentElement.scrollWidth, bad: bad.slice(0, 6) };
}"""


def check_file(page, path: Path) -> list[str]:
    doc = frame_doc(path.read_text(encoding="utf-8"))
    problems: list[str] = []
    for width in WIDTHS:
        page.set_viewport_size({"width": width, "height": 900})
        page.set_content(doc)
        page.wait_for_timeout(120)
        states = [("initial", page.evaluate(MEASURE))]
        buttons = page.query_selector_all("button")
        for i in range(len(buttons)):
            try:
                buttons[i].click(timeout=500)
            except Exception:
                continue
            page.wait_for_timeout(60)
            states.append((f"after button {i + 1}", page.evaluate(MEASURE)))
        for label, result in states:
            if result["scrollWidth"] > result["vw"] + 1 or result["bad"]:
                detail = "; ".join(result["bad"]) or f"scrollWidth {result['scrollWidth']}"
                problems.append(f"width {width} {label}: {detail}")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="files or directories (default: templates, examples)")
    parser.add_argument("--engines", default="chromium,webkit",
                        help="comma-separated Playwright engines (default: chromium,webkit)")
    args = parser.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright is not installed; see the docstring for setup", file=sys.stderr)
        return 2

    targets: list[Path] = []
    for raw in args.paths or ["templates", "examples"]:
        p = Path(raw)
        if not p.is_absolute():
            p = ROOT / p
        targets.extend(sorted(p.rglob("*.html")) if p.is_dir() else [p])

    engines = [e.strip() for e in args.engines.split(",") if e.strip()]
    failures = 0
    with sync_playwright() as pw:
        for engine in engines:
            browser = getattr(pw, engine).launch()
            page = browser.new_page()
            for path in targets:
                problems = check_file(page, path)
                rel = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
                if problems:
                    failures += 1
                    print(f"FAIL [{engine}] {rel}")
                    for problem in problems:
                        print(f"  {problem}")
                else:
                    print(f"ok   [{engine}] {rel}")
            browser.close()
    print(f"\n{len(targets)} file(s) x {len(engines)} engine(s), {failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
