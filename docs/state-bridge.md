# The Muse widget state bridge

Unofficial documentation, written from the observable behavior of Muse
chat widgets. Meta does not publish this as a stable SDK; if the behavior
changes, this document and the templates should change with it.

## Fragment shape

A widget is an HTML fragment rendered inside an iframe shell. Do not emit
`<!DOCTYPE>`, `<html>`, `<head>`, or `<body>`. The fragment is stored with
the conversation and replayed later, so it must be self-contained and at
most 1 MB. Media must not be inlined as base64 data URLs.

## State

Interactive state lives in the bridge, not in browser storage:

```js
// Seed (or read) the complete state. When no durable state exists yet,
// the bridge persists these defaults.
var state = window.hatchWidget.getState({ value: 4 });

// After every user mutation, replace the state in full.
window.hatchWidget.setState({ value: 5 });

// When state changes elsewhere, the widget is notified:
window.addEventListener('hatch-widget-state', function (e) {
  state = e.detail.state;
  render();
});
```

- `localStorage`, `sessionStorage`, IndexedDB, and cookies are not durable
  widget state and must not be used.
- Keep the whole application state in the object returned by `getState`;
  do not keep the only copy in a JavaScript closure.
- The agent that created the widget can read the same state back, which is
  what makes checklists and forms useful across turns.
- Derived values are computed during render and are never stored.

## Interactions

- Do not use `<form>` or form submission. Use buttons and inputs with
  explicit event handlers that call `setState`.
- Interactions are local: tapping a control never calls the model. A
  follow-up happens only when the user sends a new message.

## Theming

The shell sets `html[data-theme="light"]` or `html[data-theme="dark"]` and
provides these variables. Use each only for its semantic role:

| Variable | Role |
| --- | --- |
| `--hatch-widget-bg` | Outer background; may be transparent |
| `--hatch-widget-surface` | Card and control backgrounds |
| `--hatch-widget-surface-muted` | Lower-emphasis backgrounds |
| `--hatch-widget-text` | Primary text and icons |
| `--hatch-widget-muted` | Secondary text and icons |
| `--hatch-widget-border` | Borders and dividers |
| `--hatch-widget-accent` | Accent text, icons, borders, indicators |
| `--hatch-widget-on-accent` | Foreground on a filled accent surface |
| `--hatch-widget-focus` | Focus rings |
| `--hatch-widget-shadow` | Box shadows |

Never hard-code white or black for neutral UI; a widget must read correctly
in both themes.
