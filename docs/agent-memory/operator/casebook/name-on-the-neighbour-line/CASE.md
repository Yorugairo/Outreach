# The name on the neighbour's line

**The operator** (ledger `8086dab785f2`, 2026-09-13 03:11): *"it sounds like there were some engine improvements
related to albels you should improve."*

**Where:** `normal-for-which-bridge`, 0:19-0:21 - the two-line long-end page (10-year and 30-year Treasury), 9:16.

**Before** (`before.png`, review-v1, t=19.5): "10-year" is printed across the grey 30-year line above it, and the
callout's arc starting on the 4.83% datum clips the label's end. A viewer reads the name as belonging to the wrong
line.

**After** (`after.png`, build-review at 41bf55c, t=20.8): "10-year" sits under its own orange line; the 4.83% callout
has its room.

**Why it happened:** on a portrait page every terminal name is written 30 px ABOVE its own tip. With two lines close
together, the lower line's name lands on the upper line.

**The fix (41bf55c):** a portrait name whose box would cross ANOTHER series' line goes under its own line when that
room is clear - measured over the name's own width. A first try measured a fixed 330 px span, read the room under a
dipping line as taken, and put the name straight back on the neighbour; the frame caught it.

**The gate:** none - JUDGE (gate owed). M28 checks label pairs, not a label against a series path.

**The lesson for any author:** a direct label names the line it touches; if it touches two, it names neither.
