# AGENTS

This repository publishes a component catalog, ready-to-use templates, an agent skill, and a validator for interactive chat widgets in Muse (Meta's personal AI agent).

- Canonical language for public documents and the skill is English. `README.ja.md` is the Japanese companion.
- Widget templates are single self-contained HTML fragments. They must use the `--hatch-widget-*` theme variables, must not use `localStorage` or `<form>`, and keep state only through the `window.hatchWidget` bridge.
- Every template and example must pass `tools/validate-widget.py` before it is committed.
- This repository was generated from Hyd3-14/repo-template with Copier. Baseline files are updated with `copier update`; do not edit `.copier-answers.yml` by hand.
- Pull requests follow the repository PR template and carry exactly one `review:` label.
