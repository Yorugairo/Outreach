---
name: judge-the-frame-not-the-diff
description: "After any visual change, look at the rendered frame as a viewer before sending it - checking that your own change worked is not the same as judging the picture"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-08T01:52:57.695Z
---

After a visual change, render the frame and read it the way a viewer would - "can I read this page?" - BEFORE sending it.
Verifying that my own change did what I intended is not the same check, and it misses everything I did not touch.

**Why:** 2026-09-07, the operator, on a still I had just sent as if it were fine: *"this shouldn't read as approvable to you,
why does it?"* The centred card was sitting across the page's title and sub. I had confirmed the card landed and was centred,
and stopped there. The same failure repeated three more times that night: a combo page with eight bar values under two 44 px
names (a wall), a naked vertical span at the plot edge that read as a data artifact (it was a bracket whose label had no
room), and a card centred on the STAGE instead of the page, landing on the chart. Every one was visible in the first frame I
rendered. None was visible in the diff.

**How to apply:** render, then look at the whole frame and name what a viewer sees first. Ask the three questions the
operator keeps asking: does it read at a glance, does anything overlap, does anything look like a mistake. When something is
wrong, fix the cause rather than removing the thing that collided (I deleted inline series names and turned the sub into a
legend, which the very next research drop identified as the classic error - the collision was the bug, not the labels).
Judging the frame is also how the good calls arrive: every improvement the operator asked for this session came from
watching, not from reading code. Related: [ai-baselines-operator-corrects](ai-baselines-operator-corrects.md), [chart-reads-at-a-glance-e28](chart-reads-at-a-glance-e28.md),
[chart-form-rulings-e50-e53](chart-form-rulings-e50-e53.md).
