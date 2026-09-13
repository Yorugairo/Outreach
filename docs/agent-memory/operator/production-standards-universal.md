---
name: production-standards-universal
description: Finance-lane production standards (doc 29 scene-evidence lane) are THE standard for every channel; history-lane still-plate pattern is deprecated; only scripting adapts per lane
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-08-25T11:10:04.889Z
---

Operator correction (2026-08-25, Steel and Paper build): I assembled a rough
cut using the history lane's timestamped-still pattern (hard cuts between
held plates). Wrong: *"that history episode hasn't been updated for weeks.
The animation you're running is fake and looks like flashing. You have no
evidence call out. EVERY channel needs to use the standards we've developed
for finance, they'll just be ported over eventually. for theme / audience in
the scripting."*

**Why:** the finance standards (repo doc 29 — evidence-dock grammar,
momentum mechanics, linked choreography, scene-evidence lane) are the
production bar for ALL lanes. Lanes differ only in scripting (theme,
audience, voice). The history lane's doc-17 still-schedule is legacy.

**How to apply:**
- Production = doc 29 Part 8 scene-evidence lane by default: one ken-burns
  vector per scene · translucent washi docks (plate reads through chrome,
  document inside stays opaque) · badges only with verbatim-verified
  numerals · captions on canonical word timings, never resampled · wipes on
  evidence-free boundaries · linked choreography reserved for the opening
  and structured arguments.
- Never ship a cut of still frames held full-screen with hard cuts — that
  reads as flashing slides and buries the evidence layer.
- Every episode needs an evidence callout layer (docks/badges), not just
  world plates.
- Timeline is DATA generated from `scene_evidence_timeline.schema.json`
  (`build_scene_evidence_cut.py`); nobody authors motion per episode.

THE HOOK PROP IS NOT THE BRAND (operator, twice, 2026-08-25): a ring
token (e.g. Steel and Paper's railway spike) is one episode's device —
never channel/series identity, never other episodes' style reference,
and not even its own episode's thumbnail subject. Thumbnails sell the
episode's QUESTION/THESIS, not its opening prop.

Second correction round (2026-08-25, doc 29 Part 9): dynamic captions
ALWAYS (word-by-word punch at canonical timings, numerals accented) ·
plate density = runtime/12s (NOT a flat 10 — a 7-min episode needs ~38;
20s on one plate is the hard max and only with two strong docks over it;
thumbs/avatars/banners are not world plates) ·
evidence layer is SHARP vector, never soft raster; pull REAL data
(yfinance, no key) with exact source+window labels · prompt world plates
as **woodblock vox newsprint**, washi reserved for the evidence-dock
chrome only · editorial flags ([verify]) never in scripts — verification
precedes scripting; TTS strips leaks defensively · narration recorded per the
MASTER TAKE rule (repo doc 37 §8): episodes ≤~9k chars = ONE ElevenLabs
request (mv2 cap 10k chars ≈ 10 min); scene cuts are timestamps in the
words file, never audio seams; silence >1.2s lives in the edit, not the
voice; splice-repair of a broken take is banned — retake instead.

Third correction round (2026-08-25, overnight batch review): REBUILD,
don't extract — evidence charts are always rebuilt sharp from real data
(hyperframes/yfinance/cited verbatim figures with attribution); frame
extraction from third-party video is retired except the brief on-screen
citation moment, unless the source grants chart exports. "There is no
copyright on charts." Unfetchable series wait for the grant or operator
data — never eyeball-approximated. AND: work orders are IMMUTABLE after
dispatch — codex holds the old context in memory; a correction = reject
at review + open a fresh claim id, never patch a dispatched order.

Related: [ear-writing-priorities](ear-writing-priorities.md), [youtube-retention-clock](youtube-retention-clock.md)
