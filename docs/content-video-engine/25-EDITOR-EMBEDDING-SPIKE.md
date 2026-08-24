# 25 — Editor Embedding Spike: iframe Studio, or deep links?

Timeboxed evaluation (P16 T6) of embedding Remotion Studio in a console tab
versus deep-linking to it. **Recommendation: deep links. No iframe.** This doc
records the decision so it is not relitigated; per the P16 gate, an iframe
would ship only on explicit operator approval regardless of this analysis.

## Evidence

1. **Studio is an SPA that owns its full window.** The pinned 4.0.502 routes
   by `window.location.pathname` (`@remotion/studio/dist/helpers/url-state.js`;
   `getRoute()` returns the pathname, `pushUrl` drives `history.pushState`).
   Inside an iframe that history manipulation works but is invisible to the
   console shell — back/forward and reload semantics silently diverge from
   what the operator sees in the address bar.
2. **Cross-origin, by construction.** Console serves on `127.0.0.1:8765`,
   Studio on `:3000`. Different ports are different origins: no script access
   across the boundary, so the console could not read Studio state, sync
   selection, or even detect load failure — an iframe would be a dumb window
   with worse chrome than a browser tab.
3. **Websockets and fast-refresh.** Studio holds a hot-middleware websocket to
   its own dev server. Framing adds a second network topology to debug when it
   breaks, for zero functional gain.
4. **The console's own CSP posture.** The console is offline-strict (the
   off-origin structural test bans external references in templates). An
   iframe to another localhost origin survives that test literally but
   violates its spirit: the console page would depend on a second live server
   to render fully.
5. **The dual-monitor reality.** The operator triages on one screen; Studio is
   a full-window authoring tool on the other. A deep link that lands on the
   right composition (`/{CompositionId}`, verified) serves that layout better
   than a cramped embedded pane.

## What ships instead

- `studio_link()` — one tested helper building `http://127.0.0.1:<port>/<id>`
  links, rendered on Board and Runs only while Studio reports `serving`.
- The Editor view: lifecycle chips, start/stop, stderr verbatim, headless
  renders.

## Revisit triggers

Reopen this decision only if one of these becomes true: Remotion ships a
supported embedded/read-only Studio surface (the `remotion_isReadOnlyStudio`
query-string mode hints at one); the console gains multi-user or remote
operation (it will not — P15/P16 scope); or the operator asks for
single-window operation after living with deep links.
