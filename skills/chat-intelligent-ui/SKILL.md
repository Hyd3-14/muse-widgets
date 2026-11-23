---
name: chat-intelligent-ui
description: Decide when a Muse chat answer should include an interactive HTML widget instead of plain text, pick the right component from the muse-widgets catalog, and build it so its state persists and can be read back. Use when an answer involves choices, quantities, comparisons, progress, checklists, short forms, or data the user will want to adjust, tick off, or revisit.
---

# Chat Intelligent UI

A Muse chat answer is text by default. Add a widget when the answer has a
shape the user benefits from touching: sweeping a quantity, switching a
condition, ticking items off, or comparing options side by side. The
catalog, templates, and state rules live in the muse-widgets repository;
this skill is the decision layer.

## When to fire

Fire when at least one signal is present:

| Signal in the answer | Component |
| --- | --- |
| A total or result depends on one quantity the user may vary | Slider + derived value, or Calculator when several inputs interact |
| Two to five named options with different fits | Segmented control, or Conditional comparison when a table must stay fixed |
| Options the user will compare on price or features | Comparison grid (static) or Conditional comparison (interactive) |
| Steps, tasks, or a preparation list the user works through | Editable checklist |
| Progress through stages | Progress bar (static) |
| One dataset, several metrics worth viewing | Interactive chart |
| Long content in a few clear sections | Tabs |
| A few short answers to collect before acting | Input form |

When a signal matches, produce the widget by default. The exception is a
light question: a one-line factual answer stays text no matter what.

## When not to fire

- The answer is a single fact, a short explanation, or a yes/no.
- The user is mid-conversation about feelings, decisions, or wording, and a
  widget would interrupt rather than help.
- The data cannot be verified. Never embed prices, dates, or figures you
  have not checked against a live source in this conversation.
- The interaction would collect secrets, payment details, or personal
  identifiers. Widgets never do this.

## Building the widget

1. Start from the template in `templates/` of the muse-widgets repository.
   Do not write a component from scratch when a template covers it.
2. Keep state in the bridge only: seed with
   `window.hatchWidget.getState(defaults)`, replace in full with
   `setState(nextState)` after every change, re-render on the
   `hatch-widget-state` event. No `localStorage`, no `<form>`.
3. Style only with the `--hatch-widget-*` variables, 16px outer padding,
   8px radius, spacing in multiples of 4. Status is words plus color,
   never color alone. The folded card is the exception: square corners,
   no border, and its own `--pal-*` palette variables (default
   `pal-soft`) instead of the theme surface and border, because nested
   theme surfaces outlined by the theme border blend together in the
   dark theme.
4. Embed data in the fragment, separate from the drawing code. State the
   unit, period, and source of every number.
5. Write the fragment to a file, run `tools/validate-widget.py` on it,
   and fix every error before sending it. Hard-coded colors and a
   neutral surface without a `--hatch-widget-border` border are errors,
   not warnings: they are how a card becomes invisible in the dark
   theme.

## After the widget

- The widget's state persists with the conversation. On a later turn, read
  the state back instead of asking the user to repeat what they selected
  or ticked.
- Interactions are local; the model is not called when the user taps. If
  the user's next message depends on the widget, treat the read-back state
  as their input.
- When a widget turns out to be something the user will reopen, update, or
  keep data in, propose promoting it to a persistent page (a Muse Space)
  instead of regenerating widgets.
