---
name: orphan-tracking-registry
description: "What \"orphaned\" means in the animation registry, the five classifier defects fixed 2026-09-12, and the rule that a triage verdict is only real once a row carries it"
metadata: 
  node_type: memory
  type: project
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-12T15:22:20.574Z
---

**"Orphaned" is the animation registry's residual bucket**: stated in the docs, implemented nowhere, tracked by no
BACKLOG or doc-47 row, retired by nobody. Precedence is implemented > retired > tracked > orphaned. The renderer
calls it "the list to triage", and it reached 0 records on 2026-09-12 (ac5bd04) - from 46 - by fixing five defects
in the classifier and writing the four rows (R26-61..R26-64) that carry the 2026-09-05 triage's own verdicts.

**The rule the week exposed: a triage verdict is not real until a row carries it.** The 2026-09-05 triage
(`docs/content-video-engine/TRIAGE-2026-09-05.md`) had ruled RETIRE or BACKLOG on all 20 orphaned names; nobody
wrote the rows, so the registry kept reading them as unattached findings for a week and the "ranking" the counts
implied was wrong in both directions.

**The five defects, all in `build_animation_registry.py`** (each was measured before it was touched):
1. `inlined_spans` closed every KINETICS region on the module header's own prose, which quotes the marker names, so
   4286 lines of the engine's INLINED module copies read as player code. The marker is the comment, not the word;
   the parse now agrees with `sync_kinetics.REGION` exactly (29 regions, 4406 lines).
2. `template_sites` skipped any `const|let|var|function` line, so a call that assigns its result was not a call.
3. A constant object's KEY is read only as a property (`STOP.LAG_FRAMES`, `P.KEY` after `Object.assign`), and
   `word_re` refuses a dotted name, so no key was findable outside its own declaration (`key_uses` is the fix).
4. A dial named in a BLOCK comment counted as a read (`code_lines_only` runs sync_kinetics' block scan).
5. `name_tokens` gave a hyphenated law no closed form, so `arclength` in a module could not match `Arc-Length`.

**How to write a row the registry reads.** The row must contain the heading VERBATIM, em dashes included - the token
match is an exact substring and a name is matched only by its whole string unless it is a known law alias. Quote
every heading in **bold**: `retirement()` reads the status text outside the bolded titles, so a heading carrying the
word CLOSED cannot be misread as the row's verdict. The retirement vocabulary is reclassified / withdrawn / closed /
invented - the word "retired" is NOT in it - and `closed ... by <doc>` is a GRADUATION, not a withdrawal.

**Why:** the registry is the only instrument that ranks animation capability over time, so a defect in its status
classifier misreads the whole ledger; and an unattached research finding is indistinguishable from a gap.
**How to apply:** after any engine or docs change, `build_animation_registry.py --write` then `--check`; when a
record reads orphaned, decide it with a row rather than leaving it, and when a status looks wrong, read the builder
before the list.

Related: [docs-layers-and-registries](docs-layers-and-registries.md), [recall-before-propose](recall-before-propose.md), [our-artifacts-beat-outside-advice](our-artifacts-beat-outside-advice.md).
