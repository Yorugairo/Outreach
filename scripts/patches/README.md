# Patches held outside the live file

A patch lands here when a fix belongs to a file another lane holds uncommitted, so committing the file would sweep that
lane's work. The patch is the record; it applies to the committed HEAD of the file (`git apply --check`), and the lane
that owns the file folds it in when it lands.

- `cdp-driver-flow-drift-2026-09-08.patch` — the Google Flow driver's five fixes for the 2026-09-08 UI drift
  (`tools/google-flow-driver/src/cdp-driver.mjs`): Agent mode hides the settings pill (toggle it off); the Characters
  view is the authoritative character list; the media grid refills before the observer's baseline; the pill-settle
  retry; the seen image ids persist in `runtime/seen-image-ids.json` across processes. Proven live on the tariff short's
  plates; goldens untouched. Record: `docs/portable/OPERATOR-RULINGS.md` E50 amendments, `PLATE-ORDER-MAP-BEAT.md`.
