# Themes

Every component in the catalog is colored by a theme: a light/dark pair
of six role variables. Components use only the role variables, never a
theme's raw values, so swapping a theme recolors a widget without
touching its markup.

| Role | Meaning |
| --- | --- |
| `--pal-outer` | Panel background (the widget's own backdrop) |
| `--pal-inner` | Card and control surfaces on the panel |
| `--pal-fold` | Accent: filled badges, selected states, chart bars, the folded card's fold |
| `--pal-on-fold` | Text on the accent |
| `--pal-text` | Primary text |
| `--pal-muted` | Secondary text |

Separation between nested surfaces is carried by the outer/inner color
difference. Components have no borders, except hairline dividers drawn
in the opposite surface's color inside a card. (The theme border of the
host app sits too close to its surfaces in the dark theme and nested
cards outlined by it blended into the background; that failure, found
on a real device on 2026-11-23, is why this system exists.)

## Registry

One file per theme in [themes/](themes/). The Status column is the
flag that says which theme the catalog currently ships: exactly one
theme is **In use** at a time, and every template inlines that theme's
block. Other themes are variations a single widget may opt into by
inlining that theme's block instead and putting its class on the root.

| Theme | File | Use it for | Status |
| --- | --- | --- | --- |
| pal-soft | [themes/pal-soft.css](themes/pal-soft.css) | Default for ordinary diagrams (teal on soft gray / deep navy) | **In use** |
| pal-gray | [themes/pal-gray.css](themes/pal-gray.css) | Neutral, businesslike diagrams that should stay monochrome | Available |
| pal-dads | [themes/pal-dads.css](themes/pal-dads.css) | Formal or official material (DADS blue family) | Available |
| pal-warm | [themes/pal-warm.css](themes/pal-warm.css) | Reading matter and summaries (paper and rust) | Available |
| pal-pop | [themes/pal-pop.css](themes/pal-pop.css) | Gray surfaces where only the accent should stand out (orange) | Available |
| pal-note | [themes/pal-note.css](themes/pal-note.css) | Small memo-like notes (sticky-note yellow) | Available |

## Adding a variation

1. Copy an existing file in `themes/` to `themes/pal-<name>.css`, change
   the values, and keep the six roles and the light/dark pair structure.
2. Add a row to the registry above with its use and `Available` status.
3. If the theme uses colors that are not in the validator's palette
   set yet, add them to `PALETTE_HEX` in `tools/validate-widget.py`.
   Palette colors are allowed only inside a `.pal-*` rule; that scoping
   is what keeps them from leaking into ordinary styling.
4. Run `tools/validate-widget.py` and `tools/layout_check.py`.

## Switching the in-use theme

Change which theme is flagged **In use** here, then re-inline that
theme's block in every template (the block in each template is a copy
of its theme file) and rebuild the demo. Templates must never mix
themes, and a widget must never carry two theme blocks.
