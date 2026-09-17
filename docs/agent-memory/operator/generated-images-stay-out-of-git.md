---
name: generated-images-stay-out-of-git
description: "Approved plate stills, prop cutouts and every generated image stay on disk, never in git; the record (intake json, layers, manifest) is what gets committed"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-15T07:09:13.960Z
---

Generated images never go into the repo, approved or not. Approval moves a still or a cutout out of *quarantine*,
not into git: the file stays on disk (the `.gitignore` image block), and what gets committed is its record - the
intake/order json with the sha256, the `<plate>.layers.json`, a prop `manifest.json` / catalogue.

**Why:** the operator, 2026-09-15, when four split plates and 24 Gemini prop cutouts were approved: *"no, i don't
think they should go into the repo, i thought we learned that putting plate stills in the repo was a mistake?"*
The `.gitignore` says why - generated imagery is not source, is not byte-reproducible, and `.git` was already
19GB; "images already tracked stay tracked; this stops the tree growing." I had dispatched a force-add
(`git add -f`) of the four stills on the precedent of `a1b3be3` (the 2026-09-12 study stills) and stopped it
before it committed. That precedent is the mistake, not the pattern.

**How to apply:** never `git add -f` an image; a brief to release_steward names no PNG/JPG. "Out of quarantine"
= the record's review_state says approved, the file stays where it is. Recorded as E99 s31. Related:
[review-link-frozen-copy](review-link-frozen-copy.md), [gitignored-artifacts-live-in-worktree](gitignored-artifacts-live-in-worktree.md).
