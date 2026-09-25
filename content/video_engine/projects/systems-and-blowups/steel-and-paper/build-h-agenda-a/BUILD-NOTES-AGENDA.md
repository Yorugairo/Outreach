# The agenda beat both ways - P72 T42 (R26-229 (a) beside (b))

A PRIVATE build. It does not replace the committed door. `build_agenda_beds.py` (this folder) imports
`../build_episode_h.py` as a module and never edits it, then builds one bed twice from the door's own `shot_table`,
the same scratch take (`vo-h-scratch/scratch-kokoro`) and the same engine. Only the agenda beat differs.

| form | dir | rows 1-6 |
|---|---|---|
| (a) | `build-h-agenda-a/` | the page row runs to the host's dip. On "One test" the chart PARKS to 0.80 and keeps its left. The numbered agenda lands in the room that frees up, and the camera pans onto the list on "three questions" |
| (b) | `build-h-agenda-a/form-b/` | the door's rows as committed: the chart melts to a ball and splashes onto the three-notch slate, and the list lands centred on the slate's face |

The bed runs 0.00-49.45 s and ends at row 7's door (the dip into the studio, `HOST_FROM_PHRASE` "By the end"). In
both forms the three rows fire on the same words: "three questions" 43.04, "thirty" 44.09, "and it sorts" 45.62.

## Form (a)'s dials (the builder's named constants)

- `PARK_A_SCALE` 0.80 is the operator's number (E99 s82 amended again: "you could have probably shrunk 20% and been
  fine"). `PARK_A_ANCHOR` is left. The park opens 0.5 s before "One test" (41.77) and runs for 0.9 s, the same lead
  and length as the park form before `2ca4b0f`.
- `AGENDA_A_BOX` (x 0.745-0.95, y 0.20-0.62) is the freed room, measured on the parked page (probe at 42.9 s). The
  chart box is [44, 194, 1079, 604] and the end tags reach x 1414, so the room is x 1430-1824. The right edge stays at
  0.95 because a 1.06 frame is 1811 px wide and the list has to stay whole inside it.
- The pan runs from `t` 42.79 (0.25 s before "three questions") to 44.39, at zoom 1.00 to 1.06 (E99 s80 (3): the
  smallest zoom that counts as a move). The look is the list's centre (1627, 443). The frame's left edge moves 0 to 80
  px (`PAN_FRAME_X0`), so its centre drifts about 55 px toward the list while the push closes on it. That is one move,
  then still (E59 reason 2), with the camera on the thing the sentence names (s79 (3)).
- `chrome: fit` (P69 T26f, E99 s108) keeps the title, sub, source and y ticks whole in the pushed frame. The title
  starts at x 54, so without this any frame that moves toward the list would crop it (s80 (2)). The compile
  REPORTS the reach as a WARN, not a refusal: "the title (would leave at 1.043; it fits the frame) ... REPORTED - the
  frame read decides". On the frames at 44.5, 45.9 and 48.8, the title, sub, source and ticks are whole.

## Measured

- Agenda row type at rest (48.8 s), from `species/agenda.mjs agendaLayout`, where k = min(1, h/396, w/740) and the text
  is 54 x k x the camera zoom:
  - (a): k = 0.53 because the room's width binds it. That gives 30.5 stage px, about 13.5 CSS px.
  - (b): k = 0.74, bound by the slate box's height. That gives 40 stage px, about 17.7 CSS px.
  - Both clear the 12 px phone floor. On the frames, the ink height is 20-26 stage px in (a) and about 30 in (b).
- Motion gate. Both forms share the same FAIL: M11, the one the HG3 card already names ("the only mark the engine
  aims lands on the held memory line").
  - (a): 1 FAIL / 2 WARN / 16 PASS. The extra WARN is M21: "s01 19.0s (0:30 -> 0:49)". The page stays up 19 s past
    its last data mark, where E50's deployed clock is 6-8 s. The park keeps the same chart on stage through the list.
  - (b): 1 FAIL / 1 WARN / 17 PASS.
- The door is untouched. The run checks that the sha256 of `build_episode_h.py` is the same before and after, that
  `build-h/` (every file's name, size and mtime) did not move, that `SHOT-TABLE-H.md` did not move, and it runs the
  door's own read-only wall for each form. See `BEDS.json`.

## The card's proof

- `agenda-both-forms.mp4` shows (a) on the left and (b) on the right, over 40.50-49.45 s. It is 1920x540 at 24 fps,
  one headless browser per form, seeked frame by frame, with the bed's own take (`audio/episode.mp3`) under it.
- `agenda-both-forms.png` is the frame strip at 42.30 and 43.30 (enter), 45.00 (mid) and 48.80 (rest), (a) beside (b).
