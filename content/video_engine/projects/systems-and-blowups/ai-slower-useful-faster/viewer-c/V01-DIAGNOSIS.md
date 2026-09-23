# C viewer V01 diagnosis

Observed result: V01 is 7/9; [ring] w0 and [stakes] w2 are unperceived
(viewer-c/SCRIPT-C-VIEWER-FINAL.md:7,25,27). This does not show either claim
unsupported.

The scorer contract says tags sit immediately before the beat sentence
(beat_tags.py:12). It extracts the text after each tag
(viewer_score.py:170-177), maps it to a window by sentence text or overlap
(viewer_score.py:180-201), then accepts a reader line with at least two shared
content tokens (viewer_score.py:93-105, 280-293).

The frozen script instead trails tags:

- Line 1: “AI can give you a second job. [ring]”. It reads line 3,
  “Supervising the assistant you hired to save time.” Raw w0
  reader said, “AI can create a second job of supervising it.”
- Line 17: “One missed handoff makes a person inspect the output, repair it,
  and run the chain again. [stakes]”. It reads line 19, “The bottleneck is
  finished work.” Raw w2 said, “A missed handoff makes
  someone inspect the output, repair it, and run the chain again.”

The final [ring] trails the last sentence, yields no sentence, and is absent
from the nine scored beats. Conclusion: both failures are tag-position/source-
alignment failures, not unsupported claims; V01 remains binding until the
parent resolves that contract mismatch.
