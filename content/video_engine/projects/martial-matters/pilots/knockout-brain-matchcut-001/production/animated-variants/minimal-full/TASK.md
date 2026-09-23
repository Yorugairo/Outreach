# Minimal-full private-review rough cut

This directory is an isolated, editable native-SVG frame-sequence variant for
the v11 edit. It is intentionally not a migration of the shared
scene-evidence engine. The proven `../minimal-2d/` proof remains untouched.

## Acceptance criteria

- 540x960, 24fps H.264/AAC MP4 with the v11 hook/quote/follow-up/Henderson
  structure and a 2.3s reaction inserted at 8.766667s.
- Every scene has visible motion: opening proof contact/recoil/full fall,
  mouth animation in the interview, two raised-arm reaction cutouts with a
  neutral bald center, follow-up replay, and a Henderson right-hand contact
  that sends the right Bisping silhouette fully to the mat.
- Filled silhouettes, oversized gloves/heads and simple face/hair markers;
  no stick figures, gore, skulls or rasterised source art.
- On-screen disclosure is limited to the small `ANIMATED PARODY` badge, the
  real hook captions, and `SEAN SHARAF / 2019 ALLEGATION / NO CHARGES FILED.`
- `timeline.json` records contact geometry, recoil/brain rule and floor-state
  witnesses; `validation.json` records ffprobe and full decode PASS.

## Anti-goals

- No public/release-quality claim; this is private review only.
- No provider, download, credential, shared-engine, ledger, or source-footage
  changes.

Run `python render_minimal_full.py --all` to regenerate the still, frames,
audio splice, MP4, contact sheet, timeline and validation receipt.
