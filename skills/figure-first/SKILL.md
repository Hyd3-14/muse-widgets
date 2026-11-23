---
name: figure-first
description: Build Muse explanations, reports, comparisons, and decision material figure-first instead of prose-first. Use when an answer explains how something works, compares options, reports progress or results, walks through a timeline or a process, or presents data — any answer whose points have a shape (order, contrast, structure, flow, quantity) that a diagram can carry better than paragraphs.
---

# Figure First

Prose is the fallback, not the default. When an explanation has a shape —
things in order, options in contrast, parts in a structure, steps in a
flow, quantities in relation — draw that shape as a widget figure first,
and let the surrounding text shrink to one line per figure: the point the
figure makes, stated once, without repeating what the figure already
shows.

This skill is the explanation layer of the muse-widgets repository. Its
sibling skill, `chat-intelligent-ui`, covers widgets the reader operates
(sliders, checklists, forms). This skill covers figures the reader only
reads: the diagram *is* the explanation.

> Status: skeleton. The firing rules, figure-type table, and self-check
> below are the contract. Sections marked TODO are planned and not yet
> written; do not treat them as available material.

## When to fire

Fire when the material is a report, a comparison, a decision brief, a
summary, or an explanation, and at least one of its points has a shape:

| Shape in the material | Figure |
| --- | --- |
| Events or phases in order | Timeline |
| Two to four options weighed against each other | Comparison grid |
| A system, a file layout, layers, who owns what | Structure diagram (prototype in `examples/prototypes/structure-diagram.html`; layered structures only) |
| Steps that cause or enable the next step | Flow diagram (prototype in `examples/prototypes/flow-diagram.html`; vertical, branches of at most two) |
| Progress through stages, with counts | Progress bar |
| One dataset, one message (share, change, ranking) | Static chart (prototype in `examples/prototypes/static-chart.html`; horizontal bars. The catalog's Interactive chart covers the switchable case) |
| Two forms of the same material the reader should compare directly | Before/After slider (`templates/before-after-slider.html`) |
| A single result or notice with one hero value | Card |

One figure per point. If a material makes three points with three
different shapes, it gets three figures, not one figure in a fixed house
style and not three paragraphs.

## When not to fire

- A light question: a single fact, a short definition, a yes/no. Text
  stays text no matter how drawable it is.
- The user is talking through feelings, wording, or a decision out loud,
  and a figure would interrupt rather than help.
- The numbers or facts are not verified in this conversation. A figure
  makes unverified data look settled; verify first, draw second.
- The shape is invented to fill the format. If the material has no order,
  contrast, structure, flow, or quantity, it has no figure.

## Workflow

1. **Split the material into points.** Write down, in one line each, what
   each part of the answer claims. A part with no claim is decoration;
   drop it.
2. **Pick a figure shape per point** from the table above. Do not fix
   one shape for the whole answer in advance.
3. **Build each figure from its template** in `templates/` of the
   muse-widgets repository, following the build rules in the
   `chat-intelligent-ui` skill (theme block, `--pal-*` role variables,
   16px outer padding, data embedded separately from drawing code, unit
   and period stated for every number).
4. **Write one line of text per figure**: the takeaway. Do not restate
   the figure's contents in prose around it. If a sentence only repeats
   what the figure shows, delete the sentence.
5. **Run the self-check below**, then validate the fragment with
   `tools/validate-widget.py` before sending, as with any widget in
   this repository.

## Self-check

Before sending, confirm each item:

- **Standalone test**: delete the surrounding text. Does each figure
  still carry its point on its own — labels, units, and the one-line
  takeaway included in or directly under the figure?
- **No repetition**: does any prose sentence repeat content that a
  figure already shows? Remove it or shorten it to the takeaway.
- **One point per figure**: does any figure try to make two claims?
  Split it.
- **Shape fits**: is the figure's shape the material's real shape
  (order drawn as order, contrast as contrast), not a default layout?
- **Hero stands out**: one element per figure is visibly the main one;
  the rest is smaller or quieter. Everything at the same size and
  weight means nothing is the point.
- **Verified data only**: every number in a figure was checked against
  a source in this conversation, with its unit and period stated.

## Output surfaces

- **Chat widget (default)**: the figure ships as an in-chat widget
  fragment, built and validated as described above.
- **Disposable HTML file**: when the material outgrows a chat fragment
  (many figures, long report), build one self-contained HTML file from
  the same templates and themes instead of shrinking the figures.
  TODO: worked example and size guidance.
- **Muse Space**: when the material will be reopened and kept, promote
  it to a Space rather than regenerating figures per conversation.
  TODO: promotion criteria, shared with `chat-intelligent-ui`.

## Examples

Before/After pairs live in [examples/](examples/): the same material
written prose-first and figure-first, so the difference is visible
rather than described. Pair 01 (a conditional comparison) is done;
pair 02 (a timeline with a progress bar) is TODO. The pair-01 material
also ships as a single drag-to-compare widget in
`templates/before-after-slider.html`.

## Firing fixtures

[fixtures/firing-cases.md](fixtures/firing-cases.md) pins the routing
this skill is expected to produce: sample prompts with their expected
outcome (figure, and which type — or plain text). Run
`fixtures/check_fixtures.py` after editing this skill to confirm the
fixtures are still well-formed, and re-run the manual behaviour check
described there after any change to the firing rules above.

## Relationship to the sibling skill

- Reader needs to *operate* the answer (vary a quantity, tick items,
  switch a condition): `chat-intelligent-ui`.
- Reader needs to *understand* the answer (a report, a comparison, how
  something works): this skill.
- Both can fire in one answer: figures carry the explanation, an
  interactive widget carries the part the reader adjusts.
