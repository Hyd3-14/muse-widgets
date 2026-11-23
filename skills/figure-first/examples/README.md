# Figure First — examples

Before/After pairs: the same material written prose-first (Before) and
figure-first (After), using the templates and the theme flagged
**In use** in `catalog/themes.md`.

| Pair | Material | Figure shapes | Status |
| --- | --- | --- | --- |
| 01 | Comparing three plans; the recommendation depends on how much the reader uses the service | Conditional comparison | Done: [pair-01-before.html](pair-01-before.html) / [pair-01-after.html](pair-01-after.html) |
| 02 | Reporting a multi-week process and its current state | Timeline, Progress bar | TODO |

The pair-01 material is also the content of
`templates/before-after-slider.html`, which stacks the two forms in one
widget so a reader can drag between them.

Each pair ships as two fragments that both pass
`tools/validate-widget.py`. The Before fragment is plain styled text in
a card; the After fragment is the figure version with one line of text
per figure.

## Prototypes

`prototypes/` holds the candidate templates for the three figure shapes
the catalog does not have yet. All three pass
`tools/validate-widget.py`.

| Prototype | Shape | Known limit |
| --- | --- | --- |
| [structure-diagram.html](prototypes/structure-diagram.html) | Layers stacked, parts as chips inside a layer | Layered structures only; peer-to-peer relations do not fit |
| [flow-diagram.html](prototypes/flow-diagram.html) | Vertical steps with a two-way branch | Vertical only (a horizontal flow breaks at phone width); branches limited to two |
| [static-chart.html](prototypes/static-chart.html) | Horizontal bars with value labels, no axes | Bars only, up to about six; no line or scatter forms |
