---
name: tokyo-short-render
description: "Tokyo Tea Break - v2 (the hand rebuild on the approved cut's structure, E99 s77) RENDERED 2026-09-17 at 1440x2560 / 24 fps from the frozen copy c; the file of record is build-v2-frozen-c/render/tokyo-v2-full-1440p.mp4 (88.83 s, -15.1 LUFS), APPROVED TO UPLOAD by the operator (E99 s78: 'yes, it's to upload and I think the line is fine' - E67's history dial stays); the 09-09 render is superseded on the post"
metadata: 
  node_type: memory
  type: project
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-18T06:23:47.828Z
---

**2026-09-17 (late):** the operator, on the served frozen copy: *"tokyo tea looks good"*, then *"can we do the audio fix
on the voiceover?"* (chain G, E99 s54 - applied to the take for the first time: -17.96 -> -20.49 LUFS, VO_LUFS -20.5,
the bed 20 LU under), then *"render tokyo tea @ 1440p 24 fps"*. Rendered from `tokyo-tea-break/build-v2-frozen-c/`
(a frozen copy of `build-v2/`, frame-identical to the copy b the operator watched on :8771):
`build-v2-frozen-c/render/tokyo-v2-full-1440p.mp4` - 1440x2560, 24 fps (the render clock by ruling E99 s36), 2132
frames, 88.83 s, 40.2 MB, -15.1 LUFS integrated / -1.0 dBTP. Gitignored; over the app's 30 MiB upload limit, so it
is opened from the desktop, never sent through the app.

**What v2 is:** the approved cut's seven rows with today's polish - the melt into the desk plate (E88), the Meta
card thrown at "it's on your phone" and zooming up into the yield page (card-becomes-the-chart as amended, s72) in
place of the dip into a mount, the cards in the page's room, the desk plate alive (s65), E67's inks, the cues bound
(7 kept, 3 dropped by name, the melt silent), the outro as approved; cuts+dips 3 of 6 world changes (the approved
plays 4 + 2). Treatment: `tokyo-tea-break/REBUILD-TREATMENT-V2.md`; build: `build_short_v2.py` (the receipt in its
docstring; the shim on `recall_verify.resolve_ledger` is R26-197). The card: `tokyo-tea-break-v2-the-rebuild` on
the queue with the critic (9/10, 5/7) and the render path.

**Known and named:** the history of the holdings line renders `#875843` at 2.22:1 (E67's 0.45 history dial) - the
operator's dial, asked on the card; the mount at 1.99-4.0 s shows the soak's stains on cream because a cut CUTS
(R26-50, 2026-09-11 - the approved player predates it); the melt has no cue in the map (s37, nothing invented).

**2026-09-17, later:** the operator on the render: *"ea link, and yes, it's to upload and I think the line is fine"* - E99 s78: v2 is the new Tokyo, approved to upload; E67's history dial STAYS (the question is closed - never raise the 0.45 history again as a dial); the way v2 was made is the next short's way (s78 Apply 3). The direct link that served it: http://127.0.0.1:8772/render/tokyo-v2-full-1440p.mp4.

**2026-09-18:** the operator's second look with VidIQ's forecast (E99 s79): the life mechanics were missing (v2 had ONE idle token), the open goes to the axes with the tea clip docked, the camera on named things; then s80 (a second card takes the outgoing card's slot; a punch may crop the page, the caption yields). Built by hand as `build_short_v3.py`: v3 (`build-v3-frozen-a`, the panel in the left room by a park) and v3b (`build-v3-frozen-b`, the panel in the tea card's slot, the chart whole) - BOTH rendered 1440x2560 / 24 fps / 88.83 s / -15.1 LUFS and copied to Downloads (`tokyo-tea-break-v3-1440p.mp4`, `-v3b-`); the punches measured OUT (a 9:16 page's foot sits 13 px above the caption strip; no caption door for a camera key - R26-201's engine order); the 21.5x arrives as a ring on its bar (R26-190 - a figure on a bars page never renders). The critic on v3: 8/10, 4/6; its re-read on v3b pending. The upload waits on the operator's pick (v3b recommended).

**Servers:** :8771 v2 frozen b, :8772 v2 frozen c, :8773 v3 frozen a, :8774 v3b frozen b, :8766 the queue.

**The 09-09 render** (`build-short/render/`, the posted Tokyo) is superseded once the operator posts v2 - never
rebuilt (E45). See [fewer-cuts-directional-flow](fewer-cuts-directional-flow.md), [rebuild-is-not-a-base](rebuild-is-not-a-base.md), [resume-2026-09-17](resume-2026-09-17.md).
