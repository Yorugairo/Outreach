# Gate B — grouped semantic recommendation review

Snapshot: `3004f6a8a6da14a64896c91297832aba4893f0f54c53cb3aeb07446cb5da1bcc`

## Group 1 — safe recommendation

`cbm-cue-002` recommends
`silicon-antidote-s02-valuation-bubble-v1` from Silicon Antidote slide 2 into
the reviewed `teal-callout` slot on `memory-skepticism-v2`.

- Score: `26.31`; runner-up: `24.66`; lead: `1.65`.
- Thresholds: score `24.0`; minimum lead `1.5`.
- Main contributions: evidence-role compatibility `+10`, normalized concept
  overlap `+10.5`, slot compatibility `+4`, readability `+1.81`.
- Binding hash:
  `85cdd8b8c637c3be97c8c7277b72455ca6d3184b4047ae45a1ed874e8283c972`.
- The editor shows the recommendation and rationale but does not insert it
  until the operator presses **Accept evidence**.
- `recommended-binding-editor-world.png` shows the live full-frame world and
  unaccepted recommendation (`5454a6b464eda872c4f59be9747869676cd8184473cf4217b4aec6994a8c5c19`).
- `accepted-binding-live-player.png` shows the accepted crop revealed inside
  the teal card with the world hero intact and the caption in the upper-left
  safe region (`bdca45ed8d1755e5f92abe12d4cba0d9d6dc0bcd0aa7b604376dbf6a76533312`).

## Group 2 — ambiguous result correctly left unmatched

`cbm-cue-003` remains `unmatched`. The failure triptych scores `25.85`; the
RAM-ageddon crop scores `25.22`; the lead is only `0.63`, below the required
`1.5`. No proposed binding or accept action is emitted.

Binding artifact:
`aa0b2498277b2bf9dbf0a86d020d0f01939e4680d91ca098d585b91cd1e0a24d`.

## Reviewed layout roles

- Teal rail: valuation/comparison evidence.
- Navy rail: capacity-penalty/mechanism evidence.
- Orange rail: supply-shock/timeline evidence.
- Fab lower-right inset: one small manufacturing field note.

Only the first mapping is an accepted compiled proof in this milestone. The
other roles are reviewed plate-profile semantics, not silently accepted edits.
