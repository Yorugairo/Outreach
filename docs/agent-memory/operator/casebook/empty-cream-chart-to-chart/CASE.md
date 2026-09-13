# The empty cream, chart to chart

**The operator** (ledger `8086dab785f2`, 2026-09-13 03:11): *"The empty cream stage isnt supposed to be on stage
during the exits. You misinterpreted that wrong. It doesnt make sense to do that when transitioning from
chart-to-chart, that is used for mounting a ledger plate to a narrative plate."*

**Where:** `normal-for-which-bridge`, 0:34 - the CUT between the federal-load page and the interest-bill page, 9:16;
the melt at 0:25 carried the plate onto the spiral page. (Corrected 2026-09-13: this case first read a scene's `exit`
as the transition OUT of it; it names the transition INTO the scene it sits on - E47, `SCENE_EXITS`.)

**Before** (`before.png`, review-v1, t=34.4): the whole stage is empty cream with one caption, "percent. And the",
while the narration carries on. There is no chart and no world under a live sentence.

**After** (`after.png`, build-review at 41bf55c, t=34.4): the interest-bill page is already on its axes at the
cut, and its line starts drawing.

**Why it happened - a misread ruling, not an engine bug.** Earlier the same day the operator had said the inked arrival
is the exception (*"I dont think next page arrives already inked most of the time"*). The agent generalised that into
"after a suck or a melt, the next page rolls out on empty cream", withdrew the stamp that prevented it, and demoted the
gate that measured it (M31) to INFO. E73 was written on that reading. The empty cream roll-out belongs to the MOUNT: a
ledger plate arriving onto a narrative plate. Between two charts it never shows.

**The fix (41bf55c):** `stamp_transition_pages` stamps `enter=axes` on a ledger page that follows another ledger page,
whatever the transition; E73 carries the correction (2', 4').

**The gate:** M31 FAILs an empty stage at any non-dip boundary with a ledger page on both sides (`measure_stage_gaps.py` ->
`stage-gaps.json`). Measured after the fix: 0.0 s at both boundaries.

**The lesson for any author:** when a ruling narrows a default, apply it at its own width. Check which transition the
operator was talking about before changing what every transition does.
