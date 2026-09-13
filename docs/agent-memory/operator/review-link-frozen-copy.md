---
name: review-link-frozen-copy
description: "A review link (a self-watch form, a served player) points at a FROZEN copy of the build; agents build in private dirs, never into a build the operator can open"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-11T23:29:53.429Z
---

On 2026-09-11 evening the third self-watch form linked the operator to `build-short-t0` served on :8746, and
three agents rebuilt `build-short-t0` in place while the operator was watching it. They saw two cards huge and
stacked over the Ten-years chart (an agent's in-progress measured-placement build) and read it as "the whole
choreography / dock placement layer seems to have regressed". Nothing committed had regressed; the link was a
moving target.

**Why:** a build under review is evidence; evidence that changes under the reader is worse than no evidence. The
standing rule "a cut under review builds BESIDE the watched build" applies to every link handed over, not only
to the approved cut.

**How to apply:** every form / report handed to the operator ships with its own frozen build copy
(`build-short-form<N>`, `cp -r` of the exact build the tiles were read from), served on its own port, never
rebuilt; every agent dispatch names a PRIVATE build dir (`TOKYO_BUILD_DIR=build-short-<slice>`) - never
`build-short-t0` once a form has been made from it. When a served build must be stopped, stop the server and
say so in the reply. Related: [file-links-never-open](file-links-never-open.md), [judge-the-frame-not-the-diff](judge-the-frame-not-the-diff.md).
