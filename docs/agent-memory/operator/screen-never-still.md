---
name: screen-never-still
description: "Ruling E21 (2026-09-02) - visual stillness, not narration pauses, killed Steel and Paper; captions are the motion when evidence is down; opening must be the densest minute; gate_motion_density.py on the built timeline"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-03T03:07:24.957Z
---

Operator, watching episode one after a flat week: "we left way too much
space/savor moments and we don't actually have enough motion on the
screen. Captions need to be more centered and explosive; they move to
share the stage with evidence, but they ARE the motion when nothing else
is happening. We learned this lesson from Alicia at one point but I
didn't realize how important it was."

Measured: zero narration pauses >= 2s (silence was NOT the problem); 23%
of runtime in eleven >12s stretches with only Ken Burns + a lower-third
caption; the opening minute the thinnest of the video (8.6 events/min,
0.9 docks/min, a 14s still stretch from 0:57 = the first-drop point); P6
no docks. Captions turned 35/min but as a 40px band with a 5% pop.

**Why:** a viewer reads stillness as "nothing is happening" regardless of
the words; the platform reads the swipe as a verdict on the whole video.
The Alicia kinetic-caption study was filed as a caption STYLE; it was a
motion BUDGET.

**How to apply:** `gate_motion_density.py <build-dir>` (exit 1) runs at
stage 7c on every build: no stretch > 12s without a visual event beyond
Ken Burns, evidence entering <= 45s apart in every phase, 20s plate hold
ceiling, the opening minute never the thinnest, stage captions on every
still stretch once the player carries `cap_mode`. Savor = the payoff HELD
on screen, never a bare plate. The Steel and Paper re-script clears the
opening-structure gate AND this gate before recording. Caption stage
mode (centred, ~64px, per-word 1.4->1.0 pop, demote to lower-third when
a dock enters) is a pending player-template claim.
See [youtube-retention-clock](youtube-retention-clock.md), [production-standards-universal](production-standards-universal.md).

**Gates as a pipeline (P34, 2026-09-03):** one script-gate runner
`python content/video_engine/scripts/run_script_gates.py <script> --pivot "<line>" --ring <t> --counterparty <n> [--timeline build-f/timeline.json]`
writes `<script>-GATES.md` (TOOLS block, every tool's stdout, script_hash,
VERDICT) and exits 1 on any FAIL; `record_chained_take.py` /
`record_master_take.py` REFUSE a missing/stale/FAIL report (`--force
"<reason>"` logs the override into the take manifest). The build writes
`build-f/GATES-MOTION.md`; `render_episode.py` refuses a full render on
FAIL (exit 2) unless `--force`. Captions now have STAGE mode (declared per
page by the build, M08 enforced): on the rebuilt ep1 the six remaining
still stretches are dock-held or silent - they need plate life, a badge,
or a second dock, not captions. A3 = 10% of runtime (E23); G36 cycles the
whole video; G44 one rehook per unit.

