#!/usr/bin/env python3
"""Structural check for firing-cases.md.

Verifies the fixture table is well-formed: sequential IDs, Expected in
{figure, text}, Figure type in the allowed set, figure cases carry a
real figure type, text cases carry `none`, and both kinds exist. This
checks the fixtures, not an agent's behaviour; the behaviour check is
the manual procedure described in firing-cases.md.

Usage: python3 check_fixtures.py [path-to-firing-cases.md]
Exit code 0 when every case is well-formed.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ALLOWED_TYPES = {
    "timeline",
    "comparison-grid",
    "conditional-comparison",
    "structure",
    "flow",
    "progress-bar",
    "chart",
    "card",
    "before-after",
    "none",
}

ROW = re.compile(r"^\|\s*([FN]\d{2})\s*\|\s*(.+?)\s*\|\s*(figure|text)\s*\|\s*([a-z-]+)\s*\|$")


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("firing-cases.md")
    errors: list[str] = []
    seen: dict[str, list[str]] = {"F": [], "N": []}
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not re.match(r"^\|\s*[FN]\d{2}\s*\|", line):
            continue
        m = ROW.match(line)
        if not m:
            errors.append(f"line {lineno}: malformed row: {line.strip()}")
            continue
        case_id, _prompt, expected, fig_type = m.groups()
        seen[case_id[0]].append(case_id)
        if fig_type not in ALLOWED_TYPES:
            errors.append(f"{case_id}: figure type '{fig_type}' is not in the allowed set")
        if expected == "figure" and fig_type == "none":
            errors.append(f"{case_id}: expected figure but figure type is none")
        if expected == "text" and fig_type != "none":
            errors.append(f"{case_id}: expected text but figure type is '{fig_type}'")
    for prefix, label in (("F", "figure"), ("N", "text")):
        ids = seen[prefix]
        if not ids:
            errors.append(f"no {label} cases found")
        expected_ids = [f"{prefix}{i:02d}" for i in range(1, len(ids) + 1)]
        if ids != expected_ids:
            errors.append(f"{label} case IDs are not sequential: {ids}")
    total = len(seen["F"]) + len(seen["N"])
    if errors:
        print(f"NG {path.name}: {len(errors)} problem(s) in {total} case(s)")
        for e in errors:
            print(f"  error: {e}")
        return 1
    print(f"ok {path.name}: {total} cases ({len(seen['F'])} figure, {len(seen['N'])} text)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
