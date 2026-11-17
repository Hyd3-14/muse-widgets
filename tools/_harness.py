"""Shared harness for the demo builder and the layout check.

A fragment only becomes a widget inside Muse, where the app supplies the
--hatch-widget-* theme variables and the window.hatchWidget state bridge.
Tools that render fragments outside Muse must supply stand-ins for both,
or every themed element falls back to transparent and interactive
components never run. This module is the single source of those stand-ins.
"""

SHIM = """
<script>
  window.hatchWidget = (function () {
    var state = null;
    return {
      getState: function (defaults) {
        if (state === null) state = JSON.parse(JSON.stringify(defaults));
        return state;
      },
      setState: function (next) {
        state = next;
        window.dispatchEvent(new CustomEvent('hatch-widget-state', { detail: { state: state } }));
      }
    };
  })();
</script>
"""

THEME = """
<style>
  :root {
    color-scheme: light dark;
    --hatch-widget-bg: transparent;
    --hatch-widget-surface: #ffffff;
    --hatch-widget-surface-muted: #eef1f5;
    --hatch-widget-text: #1c2430;
    --hatch-widget-muted: #5b6572;
    --hatch-widget-border: #d3d9e1;
    --hatch-widget-accent: #0017c1;
    --hatch-widget-on-accent: #ffffff;
    --hatch-widget-focus: #0017c1;
    --hatch-widget-shadow: 0 1px 4px rgba(16, 24, 40, 0.12);
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --hatch-widget-surface: #1f2530;
      --hatch-widget-surface-muted: #272f3d;
      --hatch-widget-text: #f2f4f7;
      --hatch-widget-muted: #a7b0be;
      --hatch-widget-border: #3a4356;
      --hatch-widget-accent: #7ea2ff;
      --hatch-widget-on-accent: #0a0f1e;
      --hatch-widget-focus: #7ea2ff;
      --hatch-widget-shadow: 0 1px 4px rgba(0, 0, 0, 0.45);
    }
  }
  body { margin: 0; }
</style>
"""


def frame_doc(fragment: str, extra_body: str = "") -> str:
    """Wrap a fragment in a full document with the Muse stand-ins."""
    return ("<!DOCTYPE html><html><head><meta charset='utf-8'>"
            + THEME + SHIM + "</head><body>" + fragment
            + extra_body + "</body></html>")
