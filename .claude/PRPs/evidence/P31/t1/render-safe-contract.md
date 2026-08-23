# P31 T1 — render-safe display contract

- General authored overlays expose `display_text`.
- Citation overlays expose `citation_id` and `diagnostic_label`, remain locked,
  and do not contain `text` or `display_text`.
- Normal rendering does not fall back to labels, item IDs, source refs, or
  citation IDs.
- Diagnostic copy requires the top-level `diagnosticMode` composition flag;
  item props cannot enable it.
- Transcript captions retain protected canonical `text`, word indices, and
  timing; `caption_preset` is additive.

Verification on 2026-08-11:

- Python compiler/contracts: `7 passed in 5.92s`.
- Remotion editor: typecheck passed; `11 passed`.
- Production console: typecheck passed; `19 passed`.
