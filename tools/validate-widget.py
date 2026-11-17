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
HARDCODED_BG_RE = re.compile(r"background(?:-color)?\s*:\s*#[0-9a-fA-F]{3,8}\b")


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
    if HARDCODED_BG_RE.search(text):
        warnings.append("hard-coded hex background color; prefer the --hatch-widget-* theme variables "
                        "so the widget works in both light and dark themes")
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
