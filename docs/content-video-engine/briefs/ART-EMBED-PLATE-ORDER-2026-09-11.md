# The ART-embed plate - the order for human gate 3 (P50 T7, 2026-09-11; the style line corrected to the house atom the same day)

**What the gate asks.** P50 T7 gives the external lane its world: Bravos has the chart world and the TV world (their
claims on a monitor in a lit studio); we have the chart world (the ledger page) and the ART world (our narrative
plates). The first narrative plate that carries a declared embed SURFACE - a poster on the wall, a paper on the desk, a
framed picture - needs a Flow order (the standing rule: ask before driving the Flow session) or a still the operator
generates by hand, as with the fab plate. This is that order, for a yes, a no, or a hand-made still.

**What the plate must carry.** ONE flat surface inside the painting, facing the viewer at a slight angle, large enough
that a press card projected onto it reads on a phone (the surface at least 40 % of the stage's width, its long side
near horizontal, no more than ~12° of perspective on either axis - a homography can sell more, the type cannot). The
surface is BLANK in the painting (E33 / doc 15 §4: no facts, dates, labels or quotations inside generated pixels -
the information layer is composited afterward). The rest of the plate is the house world. The embed surface is one flat plane facing the viewer, so the order carries no "Layered 2.5D near / mid / far plane" context phrasing (that is for plates that need parallax).

**The order (Money Physics; the style atom verbatim from `docs/portable/OPERATOR-RULINGS.md` E37's amendment of 2026-09-08 - "from this date every new plate order uses the amended sentence"; portrait 9:16 first, a landscape sibling if cheap):**

> A quiet study at night. A light application of 2.5D woodblock print and vox newspaper meets rich anime colors.
> A wooden desk in the lower third with a mug and a folded newspaper; on the wall above it, centred, a large
> blank poster in a thin dark frame, its face slightly angled toward the viewer, catching the lamp's light. Nothing
> printed on the poster. A desk lamp on the left throws a warm cone across the wall; the corners fall to shadow. No
> people, no text anywhere in the image, no logos.

Two more surfaces worth a second still if the first works: **a paper on the desk** (the card lands flat, the camera
above - a "document" embed for records) and **a framed picture on a shelf** (small, for a single stamp).

**What the engine does with it (T7's code, built against a synthetic quad until the plate exists).** The plate's
manifest declares `embed: {quad: [[x, y] x 4] (stage fractions, the surface's corners in order TL TR BR BL), darken:
"<word>"}`. A press dock with `embed: True` on that plate is projected onto the quad by a planar homography (the CSS
`matrix3d` from the four corners; Gemini's H with h22 = 1); the room's vignette darkens on the word so the surface
lights; the card's own idle stays; its badges and underline live in the projected space. The argument's own charts
never embed (B1: their claim on their surface; ours on the page).

**What I need from you.** One of: (1) "order it" - I drive the Flow session for this prompt and bring back the still
for your pick; (2) a still you make by hand at 1080x1920 (the surface's corners I will measure); (3) "not now" - T7's
code ships against the synthetic quad and the plate waits.
