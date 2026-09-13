# The ring on the tip label

**The operator** (ledger `8086dab785f2`, 2026-09-13 03:11): *"it sounds like there were some engine improvements
related to albels you should improve."*

**Where:** `normal-for-which-bridge`, 0:57 - the ring sentence "This one carries...", 9:16.

**Before** (`before.png`, review-v1, engine at a54c217): the dashed 123% ring on the last datum sits on the end of the
line's own name, "x3.9 Federal debt" - the word "debt" runs into the ellipse. Every gate passed: M28 checks a page's
labels against each other, and the ring is a species painted on its own layer.

**After** (`after.png`, build-review, engine at 41bf55c): the name ends clear of the ring's reach.

**Why it happened:** the line builder writes its terminal name 8 px left of the last point, and the last datum is the
point a ring or callout marks most often. A ring round a point is at least 54 px wide (RING.MIN_RX), and it widens
further when it hugs nearby ink (`ringMark` takes in ink up to e.rx back, then pads it again) - 72 px of clearance
was still measured 36 px short on this frame.

**The fix (41bf55c):** the compiler stamps `tip_mark: [series]` on a page whose ring or callout targets a line's last
datum (`stamp_tip_marks`, `build_scene_timeline_f.py`); the line builder ends that name 110 stage px left of the tip.
Unmarked pages draw as before.

**The gate:** none - JUDGE (gate owed). Nothing measures a terminal label against a species' ellipse; the layout probe
could, from the ring's resolved box and the name's DOM box.

**The lesson for any author:** the most-marked point on a chart is the end of its line; anything written next to it
has to leave room for the mark it will get.
