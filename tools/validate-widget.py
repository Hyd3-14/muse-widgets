#!/usr/bin/env python3
"""Validate Muse chat widget HTML fragments against the widget contract.

Usage:
    python3 tools/validate-widget.py [file-or-dir ...]

With no arguments, validates templates/ and examples/ of this repository.
Exit code is 1 when any error is found. Warnings never fail the run.

The contract (see docs/state-bridge.md):
  - A widget is an HTML fragment, not a full document.
  - State lives only in the window.hatchWidget bridge.
  - No localStorage, sessionStorage, IndexedDB, or document.cookie.
  - No <form> elements; interactions use explicit event handlers.
  - A fragment must not exceed 1 MB.
  - Colors come from the --hatch-widget-* theme variables, never from
    hard-coded literals. A literal that happens to look right in one
    theme is invisible in the other: a near-black border on a dark
    surface was the failure that prompted this rule. The only allowed
    literals are the Okabe-Ito category colors (plus their paired ink),
    which have no theme variable and are defined as light/dark pairs.
  - An element filled with a neutral surface color must carry a border
    in --hatch-widget-border (or --hatch-widget-accent) in the same
    declaration block, so its outline survives both themes.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

MAX_BYTES = 1_000_000

ERROR_PATTERNS: list[tuple[str, str]] = [
    (r"<!DOCTYPE", "full document: <!DOCTYPE> is not allowed in a fragment"),
    (r"<html[\s>]", "full document: <html> is not allowed in a fragment"),
    (r"<head[\s>]", "full document: <head> is not allowed in a fragment"),
    (r"<body[\s>]", "full document: <body> is not allowed in a fragment"),
    (r"\blocalStorage\b", "localStorage is not durable widget state; use window.hatchWidget"),
    (r"\bsessionStorage\b", "sessionStorage is not durable widget state; use window.hatchWidget"),
    (r"\bindexedDB\b", "IndexedDB is not durable widget state; use window.hatchWidget"),
    (r"document\.cookie", "document.cookie must not be used for widget state"),
    (r"<form[\s>]", "<form> is not allowed; use buttons and explicit event handlers"),
]

INTERACTIVE_RE = re.compile(r"<(input|button|select|textarea)[\s>]|onclick|addEventListener")
RULE_RE = re.compile(r"([^{}]+)\{([^{}]*)\}")
INLINE_STYLE_RE = re.compile(r"""style\s*=\s*"([^"]*)"|style\s*=\s*'([^']*)'""", re.IGNORECASE)


def overflow_risks(text: str) -> list[str]:
    """width:100% plus padding/border without border-box overflows the parent.

    A file is safe when every such rule carries its own
    `box-sizing: border-box`, or when a universal rule (a selector list
    containing `*`) sets border-box for all descendants.
    """
    style_blocks = re.findall(r"<style[^>]*>(.*?)</style>", text, flags=re.IGNORECASE | re.DOTALL)
    rules: list[tuple[str, str]] = []
    for block in style_blocks:
        rules.extend(RULE_RE.findall(block))
    universal = any(
        "*" in selector and "box-sizing" in body and "border-box" in body
        for selector, body in rules
    )
    risks: list[str] = []
    candidates = [body for _, body in rules]
    candidates += [a or b for a, b in INLINE_STYLE_RE.findall(text)]
    for body in candidates:
        if not re.search(r"width\s*:\s*100%", body):
            continue
        if not re.search(r"padding|border", body):
            continue
        if "box-sizing" in body and "border-box" in body:
            continue
        if universal:
            continue
        risks.append(body.strip()[:60])
    return risks
ALLOWED_HEX = {
    "0072b2", "56b4e9", "d55e00", "e69f00", "009e73",
    "35c48d", "cc79a7", "e39ac2", "1a1a1a",
}
HEX_RE = re.compile(r"#([0-9a-fA-F]{3,8})\b")
FUNC_COLOR_RE = re.compile(r"\b(?:rgba?|hsla?)\([^)]*\)", re.IGNORECASE)
COLOR_PROPS = {
    "color", "background", "background-color", "border", "border-color",
    "border-top", "border-right", "border-bottom", "border-left",
    "border-top-color", "border-right-color", "border-bottom-color",
    "border-left-color", "outline", "outline-color", "box-shadow",
    "fill", "stroke", "text-decoration-color", "caret-color",
}
NAMED_COLORS = {
    "black", "white", "gray", "grey", "darkgray", "darkgrey", "dimgray",
    "dimgrey", "lightgray", "lightgrey", "silver", "red", "green", "blue",
    "navy", "teal", "orange", "purple", "pink", "brown", "yellow",
    "magenta", "cyan", "lime", "maroon", "olive",
}


def style_sources(text: str) -> list[str]:
    """Every place CSS can hide: <style> blocks and style attributes,
    including style attributes inside script-built HTML strings."""
    sources = re.findall(r"<style[^>]*>(.*?)</style>", text,
                         flags=re.IGNORECASE | re.DOTALL)
    sources += [a or b for a, b in INLINE_STYLE_RE.findall(text)]
    return sources


def declarations(body: str) -> list[tuple[str, str]]:
    decls = []
    for chunk in body.split(";"):
        if ":" not in chunk:
            continue
        prop, value = chunk.split(":", 1)
        decls.append((prop.strip().lower(), value.strip()))
    return decls


def hardcoded_color_errors(text: str) -> list[str]:
    """Hard-coded color literals in CSS, as errors.

    Hex values are matched anywhere in a style source. Functional
    notations (rgb/hsl) likewise. Named colors are matched only as the
    value of a color-bearing property, so prose and font names are safe.
    """
    errors: list[str] = []
    seen: set[str] = set()

    def add(message: str) -> None:
        if message not in seen:
            seen.add(message)
            errors.append(message)

    for source in style_sources(text):
        for match in HEX_RE.finditer(source):
            raw = match.group(1).lower()
            norm = raw
            if len(norm) == 3:
                norm = "".join(c * 2 for c in norm)
            elif len(norm) == 8:
                norm = norm[:6]
            if len(norm) == 6 and norm not in ALLOWED_HEX:
                add(f"hard-coded color #{raw}; use a --hatch-widget-* "
                    f"theme variable so the widget works in both themes")
        for match in FUNC_COLOR_RE.finditer(source):
            add(f"hard-coded color {match.group(0)}; use a "
                f"--hatch-widget-* theme variable so the widget works "
                f"in both themes")
        for prop, value in declarations(source):
            if prop not in COLOR_PROPS:
                continue
            for word in re.findall(r"[a-zA-Z]+", value.lower()):
                if word in NAMED_COLORS:
                    add(f"hard-coded color '{word}' in {prop}; use a "
                        f"--hatch-widget-* theme variable so the widget "
                        f"works in both themes")
    return errors


def surface_border_errors(text: str) -> list[str]:
    """A neutral surface fill without a theme border in the same block.

    The surface variables sit close to the app background by design, so
    the border is the only thing that keeps a card's outline visible,
    especially in the dark theme. Pseudo-state rules (:hover and the
    like) are skipped: they restyle an element whose base rule carries
    the border.
    """
    errors: list[str] = []
    blocks: list[tuple[str, str]] = []
    for block in re.findall(r"<style[^>]*>(.*?)</style>", text,
                            flags=re.IGNORECASE | re.DOTALL):
        blocks.extend(RULE_RE.findall(block))
    blocks += [("(inline style)", a or b)
               for a, b in INLINE_STYLE_RE.findall(text)]
    for selector, body in blocks:
        if ":" in selector and not selector.startswith(":"):
            continue
        decls = dict(declarations(body))
        bg = decls.get("background", "") + " " + decls.get("background-color", "")
        if "var(--hatch-widget-surface" not in bg:
            continue
        border_values = [v for p, v in declarations(body)
                         if p == "border" or p.startswith("border-")]
        visible = [v for v in border_values
                   if not re.search(r"\b(none|hidden|0)\b", v.split("solid")[0])
                   and re.search(r"\b(solid|dashed|dotted|double)\b", v)]
        if not visible:
            errors.append(
                f"neutral surface without a border ({selector.strip()[:40]}); "
                f"add border: 1px solid var(--hatch-widget-border) so the "
                f"outline survives the dark theme")
        elif not any("var(--hatch-widget-border)" in v
                     or "var(--hatch-widget-accent)" in v
                     for v in border_values):
            errors.append(
                f"border on a neutral surface does not use "
                f"--hatch-widget-border ({selector.strip()[:40]}); a "
                f"same-tone border is invisible on the surface")
    return errors


def validate(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    raw = path.read_bytes()
    if len(raw) > MAX_BYTES:
        errors.append(f"size: {len(raw)} bytes exceeds the 1 MB limit")
    text = raw.decode("utf-8", errors="replace")

    for pattern, message in ERROR_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            errors.append(message)

    for risk in overflow_risks(text):
        errors.append(f"overflow risk: width:100% with padding/border but no "
                      f"box-sizing: border-box ({risk}...)")
    if INTERACTIVE_RE.search(text) and "hatchWidget" not in text:
        warnings.append("interactive elements found but window.hatchWidget is never used; "
                        "state will not persist")
    if "hatchWidget.setState" in text and "hatchWidget.getState" not in text:
        warnings.append("setState is used without getState(defaults); "
                        "initial state will not be seeded")
    errors.extend(hardcoded_color_errors(text))
    errors.extend(surface_border_errors(text))
    for match in re.finditer(r"""(?:src|href)\s*=\s*["'](https?://[^"']+)["']""", text):
        warnings.append(f"external resource {match.group(1)}: only stable public URLs survive replay; "
                        "signed or expiring URLs will break")
    return errors, warnings


def collect(paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for item in paths:
        p = Path(item)
        if p.is_dir():
            files.extend(sorted(p.rglob("*.html")))
        elif p.is_file():
            files.append(p)
        else:
            print(f"not found: {item}")
            raise SystemExit(2)
    return files


def main(argv: list[str]) -> int:
    targets = argv[1:] or ["templates", "examples"]
    files = collect(targets)
    if not files:
        print("no HTML files found")
        return 2
    failed = 0
    for path in files:
        errors, warnings = validate(path)
        status = "ERROR" if errors else "ok"
        print(f"{status} {path}")
        for message in errors:
            print(f"  error: {message}")
        for message in warnings:
            print(f"  warning: {message}")
        if errors:
            failed += 1
    print(f"\n{len(files)} file(s) checked, {failed} with errors")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
