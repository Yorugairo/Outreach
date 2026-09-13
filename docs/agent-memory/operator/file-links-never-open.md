---
name: file-links-never-open
description: The operator cannot open file links to worktree paths from the chat; localhost URLs and hosted artifacts work - deliver review material that way
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-03T06:19:23.890Z
---

Operator, 2026-09-03: "i can't open any of your links from my location,
this keeps happening ... localhost works, but your file links for some
reason never actually open from your worktree."

**Why:** the desktop app resolves markdown file links against the main
checkout (`C:\Users\Snipe\Downloads\Outreach Program`), not the worktree
the session runs in, so every relative or worktree path 404s; absolute
Windows paths are not clickable either. This had already happened once
earlier in the session ("may have been deleted or moved").

**How to apply:**
- Anything the operator must LOOK at: publish it as an Artifact (hosted
  page; self-contained HTML up to 16MB, images as data URIs) or serve it
  on localhost (`preview_start` episode-player on :8731 serves build-f)
  and give the URL. Send images/PDFs with SendUserFile.
- Never rely on a markdown link to a repo file. Give paths only as
  copy-paste text in a code block, and say which checkout they are in.
- For a review pass: one hosted page that links the proofs, embeds the
  filmstrips, and lists the decisions (done 2026-09-03: "Money Physics
  Review Pass" artifact).
See [worktree-read-scope](worktree-read-scope.md), [cause-outcome-brevity](cause-outcome-brevity.md).
