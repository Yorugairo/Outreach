# Video-engine backlog discipline

Status: current. Last reviewed 2026-09-25 (the P72 T0 second pass).

## Board contract

- `BACKLOG.md` is the canonical active queue. Its opening tables organize work
  by execution context: running PRP, human review, triggered backlog, and
  bounded experiments.
- The historical source ledger lives in the same-directory
  `BACKLOG-HISTORY-2026-09.md`; keep the working board compact and do not treat
  old status tokens or line citations as current evidence. Its provenance
  banner maps original `BACKLOG.md` line references into the history file.
- Stable IDs remain attached to their work. R26 rows keep the original
  diagnosis and citations in the historical ledger; the active index names
  only current next actions.
- Every active row records a state, owner or trigger, next action/acceptance,
  and evidence pointer. Add `@intent` / `@acceptance` when the work is not
  obvious from its title and evidence.
- A code change does not close a visual task. Operator frame/audio review and
  production approval stay active until their own evidence is recorded.
- If a completed row contains a remaining question, split that question into
  one active ID and link it before archiving the completed portion.
- Use these states consistently: `🔄 In progress`, `🟡 partial or awaiting
  evidence`, `❓ revalidate/decision needed`, `⏸️ triggered or deferred`,
  `🧪 explore`, `✅ verified complete`, `🚫 withdrawn/retired`.
- Archive only when the evidence identifies the relevant artifact, measured
  result, test, commit, or operator ruling and no unresolved follow-up remains
  on that row. Preserve the source history and cross-reference split follow-up.
- Deduplicate only identical work and acceptance. Retain both old IDs as
  aliases or explicit cross-references. Similar subject matter is not enough.
- Keep new modeling research in the triggered backlog or Explore lane until a
  local comparison or measured trigger justifies implementation. Research
  claims and vendor performance numbers are not acceptance evidence.

## Context grouping

- **Running execution:** the PRP or lane owns sequencing; list its child R26 IDs
  once and update them when their own proof lands.
- **Human review:** group only frames/sound reads that share one review event;
  leave unresolved visual decisions visible after implementation completes.
- **Triggered backlog:** state the concrete trigger and first acceptance so a
  deferred idea does not masquerade as current sprint work.
- **Explore:** define a bounded A/B, matched inputs, comparison measures, and a
  promotion decision. Do not mix exploration with implementation status.

## First-pass cleanup report

**Before:** `BACKLOG.md` had 862 lines and 274 unique R26 row headers, plus one
additional `R26-248` mention without its own row; it had no canonical
active-queue table or completed archive. The P45 research triage records 54
decisions (5 TOP, 31 BACKLOG, 6 EXPLORE, 12 RETIRE). The skill-default
`Consultant input/SPRINT_BACKLOG.md` is absent in this repository; no competing
board was created. Registry examples were read-only references.

**After:** the opening board has 20 active/triggered rows and 42 active IDs:
the P69 umbrella with its 22 open child IDs, 13 legacy follow-ups, three ME-BL
items, two ME-EXP experiments, and one legacy-revalidation handoff. Thirty
evidence-backed records are indexed in the September archive and excluded from
the canonical active tables. Their original rationale and evidence remain in
the historical source ledger; all 274 R26 source-row headers are preserved. Nothing
was deleted. The extra R26-248 mention remains an unresolved reference, not a
reconstructed task.

**Archived IDs (30):** R26-63, R26-64, R26-67, R26-68, R26-69, R26-70, R26-71,
R26-74, R26-75, R26-77, R26-78, R26-79, R26-90, R26-92, R26-93, R26-94,
R26-95, R26-96, R26-97, R26-98, R26-99, R26-100, R26-101, R26-107,
R26-110, R26-112, R26-113, R26-114, R26-125, R26-262. Evidence per ID is recorded in
[`backlog/archive/2026-09-completed.md`](backlog/archive/2026-09-completed.md).
The R26-66 P57 hand-off is not archived; its operator found a jump without a
transformation, so the sequence and frame review remain active. R26-64's
remaining motion-sharpness question is tracked under R26-85. The caption
default and race-path default remain separate active questions under R26-123
and R26-124.

**Deduplication:** R26-64's remaining strobe-threshold/sharpness investigation
points to R26-85 and is represented there once. R26-77's variant implementation
is archived while its compiler-default follow-up stays under R26-123. R26-78's
two-path implementation is archived while the unresolved default question is
under R26-124. R26-125's review event is archived after its hand-off follow-up
was split to R26-66. P45 O8 and P45 T1 are the same ARAP/polar-decomposition
item; the original ledger already maps both to P38 T4, so neither is duplicated
in the active queue. R26-48 and R26-57 remain separate pending evidence that
their scopes are identical.

**Ambiguous rows left visible:** R26-31 (next Bravos selection not recorded),
R26-35/36 (sound fixes wait for a new listened pass), R26-43/44/45 (each is
triggered by a concrete future cut), R26-52 (current closure not verified),
R26-57 (possible overlap with R26-48, not proven), R26-65 (partially built
default), R26-66 (operator saw a jump), R26-85 (real-motion review pending),
R26-123 (chosen blend is not yet the compiler default), and R26-124 (the
review record does not name the race path default). `R26-248` is referenced
without its own row header. A mechanical census of the trailing status cells
found 102 rows with completion-like tokens: 29 of the 30 archive IDs overlap
that census; R26-107 is archived on direct test evidence without a matching
token. R26-123 remains active because its compiler-default follow-up is open.
The 72 other close-marked rows are listed for later review; a status token is a
triage signal, not proof that the work is complete.

**Files changed:** `BACKLOG.md`, `BACKLOG-DISCIPLINE.md`,
`backlog/archive/2026-09-completed.md`, and this worktree's existing
`docs/WORKTREE-REGISTER.md` row. No engine, PRP, ruling, media, or generated
docs-layer files were edited.

## Second-pass report — P72 T0 (2026-09-25)

The closing pass of `.claude/PRPs/plans/P72-THE-BACKLOG-BURNDOWN.plan.md` (T0). Its check is a live read, not a list:
the universe is every `| **R26-N**` history row minus the archive's first column, plus the active board's IDs, plus
every open task of P54 and P68-P72 and their human gates, plus every open review-queue item; each must map to a
carrier (an archive row, an open slice that names it, a gate row, a `⏸️` row with its trigger, or another lane's
owner). A row filed after the plan is in the universe by construction - R26-330 and R26-341..348 were found that way
and carried by the plan at `0d2e705`.

**Before (lane A `311aad7`):** `BACKLOG.md` 69 lines / 13,860 bytes; the active queue 17 rows (26 across the three
tables), 85 unique first-column IDs (74 R26); the archive 32 IDs (the first pass's 30, `DOCS-BL-01`, R26-239); the live
universe 449 items, 170 of them with no carrier.

**After:** `BACKLOG.md` 81 lines / 19,850 bytes; the active queue 29 rows (38 across the three tables), 193 unique
IDs (172 R26) - every open R26 ID listed once, under the plan or gate that carries it; the archive 178 IDs (+146:
batch 1 70, batch 2 53, batch 3 20, part 2 3); the live universe 313 items, 0 with no carrier.

**Archived IDs (146):** batch 1 (DONE-UNCLOSED): R26-0, R26-1, R26-3, R26-4,
R26-5, R26-6, R26-7, R26-8, R26-10, R26-12, R26-13, R26-16, R26-17, R26-18,
R26-19, R26-20, R26-22, R26-23, R26-24, R26-25, R26-26, R26-27, R26-28, R26-30,
R26-32, R26-34, R26-37, R26-38, R26-39, R26-40, R26-41, R26-42, R26-46, R26-47,
R26-48, R26-49, R26-50, R26-51, R26-53, R26-54, R26-55, R26-56, R26-58, R26-60,
R26-76, R26-80, R26-82, R26-83, R26-84, R26-86, R26-87, R26-89, R26-91,
R26-103, R26-104, R26-108, R26-109, R26-117, R26-118, R26-119, R26-120,
R26-121, R26-122, R26-126, R26-127, R26-131, R26-133, R26-134, R26-156,
R26-158. Batch 2 (DONE-UNCLOSED): R26-159, R26-172, R26-177, R26-179, R26-184,
R26-190, R26-191, R26-201, R26-205, R26-210, R26-211, R26-213, R26-218,
R26-220, R26-221, R26-222, R26-223, R26-224, R26-225, R26-226, R26-228,
R26-230, R26-231, R26-232, R26-233, R26-234, R26-235, R26-236, R26-241,
R26-245, R26-246, R26-247, R26-263, R26-272, R26-273, R26-276, R26-279,
R26-280, R26-282, R26-290, R26-291, R26-293, R26-295, R26-296, R26-297,
R26-298, R26-300, R26-305, R26-306, R26-308, R26-310, R26-312, R26-314 (R26-308
/ 310 / 312 / 314 as code landed, read at P71-HG1 - a code change does not
close a visual task). Batch 3 (CLOSE-STALE / -SUPERSEDED / -DUPLICATE): R26-11,
R26-31, R26-45, R26-59, R26-62, R26-65, R26-81, R26-102, R26-124, R26-155,
R26-180, R26-185, R26-186, R26-187, R26-192, R26-194, R26-196, R26-199,
R26-204, R26-216. Part 2: R26-176, R26-181 (each with its leftover closed: P65
T6 by D3 and the two lab cards withdrawn; P67 HG1's question folded into
P69-HG4) and LEGACY-REVALIDATION-2026-09. Evidence per ID - the sha, file:line
or ruling, every sha resolved with `git log -1` - is in
[`backlog/archive/2026-09-completed.md`](backlog/archive/2026-09-completed.md).

**`⏸️` IDs (7):** R26-44 ("Ask on the first cut that threads a line"), R26-52 and R26-137 ("Japan will be
re-rendered eventually, but it's not a concern right now", E99 s34), R26-61 ("THE TRIGGER: the first short that asks
a figure to gesture, bend or hold weight"), R26-15 ("The lessons named for a slice when a short asks"), R26-214 (c)
(decision D4: no ambient-lane order until a cut asks) and R26-111 (blocked on an outside step: the operator's word or
a cut that needs the plate). None of them is archived.

**Moved to their verdicts:** R26-31, R26-45, R26-65 and R26-124 archived (batch 3; R26-124 records both race paths
selectable and the engine's default `eased`); R26-35 and R26-36 active on P72 T20 and R26-43 on P72 T17 (open engine
work, no longer `⏸️`); R26-57, R26-85 and R26-123 children of the P72 row (T27, T32, T27); R26-66 with R26-88 on the
other lane's row (`MP-NORMAL-OUTREACH`); R26-52 a `⏸️` row; `LEGACY-REVALIDATION-2026-09` closed (archived).

**Held open by rule (a half is open; its slice carries it):** R26-281 and R26-283 (the camera halves are done at
`af869b7`; the row-1 and row-15 re-aims are P72 T36), R26-219 (T43, T3), R26-9 (TR-3, T27), R26-143 (T17), R26-36
(T20, a listened pass), R26-132 (T7), R26-202 (T7 / T19 / T4), R26-229 ((a), T42).

**The five parent decisions (P72 T0, each with its reason there):** D1 the long form keeps the `phone` preset (R26-316;
`longform:phone` is the only preset that holds the brace's floor, R26-339); D2 build `rel: pin` only (R26-105; R26-267
needs it); D3 P65 T6's promotion closed (recipes are proved as beats in proof doors; the defaults come from rulings);
D4 no ambient-lane order for a breathing host until a cut asks (R26-214 (c), a `⏸️` row); D5 R26-102 closed on E99
s13, R26-9 closed after its TR-3 lands in T27. Not a decision: M38 (R26-168) stays the interim WARN until the operator
answers on P72-HG1's sheet.

**Findings:** no inventory verdict was contradicted by its evidence. R26-1's history note ("the halo as such not
built") is stale - `LP_HALO` is in the engine; R26-108's H timeline count moved to 27 scenes / 25 with species / 15
with pages after row 24 and the outro landed (the claim holds); the inventory's grouped P50 wording ("SHIPPED with P50
T<n>") is not literal on R26-27 / 30 / 39 / 40, so each archive row quotes its own closing phrase.

**Files changed:** `BACKLOG.md`, this report, `backlog/archive/2026-09-completed.md` (batches 1-3, part 2 and the
census paragraph reconciled), `review-queue.v1.json` (and the regenerated `REVIEW-QUEUE.md`), the plan status lines
of P47, P48, P50, P51, P53, P54, P65, P67, P68 and P69, P72 itself, and `docs/WORKTREE-REGISTER.md` (lane B's row).
The history file is not edited: its banner pins the source slice's sha256, so the archive row is the closure.

## History split audit — 2026-09

This phase mechanically moved the old historical tail out of the working board;
it did not re-triage or rewrite that payload. The source snapshot is
`c6a589961ff8843b9e4290d82776a43ac018a3de`. Before the split, `BACKLOG.md` was
921 lines / 451,982 bytes. Original lines 55–921 (867 lines / 443,398 bytes)
now follow the seven-line provenance banner in `BACKLOG-HISTORY-2026-09.md`.
The exact moved bytes still hash to
`e45dbe006ba253cb5627efb55277309c36049bbfefa1b9b2e9535c6c7611b9f2`.

After the split, the active board is 64 lines / 9,696 bytes and the history
file is 874 lines / 443,917 bytes. Mechanical line assertions passed for original line 55
→ history line 8, line 218 → 171, and line 921 → 874; each compared equal to
the source snapshot. The source-slice hash and R26 census are unchanged: 275
unique R26 references remain in the historical tail. The canonical board has
21 data rows across its three tables, 43 unique IDs in the first column (35
R26 IDs), and no repeated first-column ID. All five ME-BL / ME-EXP IDs remain
in the active queue and source history. The completed archive still has 30
unique archived IDs. The old
`#model-engine-research-routing--2026-09-23` deep link resolves to the retained
compatibility heading on the short board.

There are 266 external `BACKLOG.md:<line>` citations in 19 documents, plus 25
historical self-citations in the moved payload. The external references all
point into original lines 55–921, so the `n - 47` mapping keeps them resolvable;
they were deliberately not rewritten. The moved file's relative-link audit
found 33 Markdown link occurrences (29 unique targets) and no broken local
targets. This separates the known historical references from genuinely broken
links; none were identified in the moved slice.

**Verification:** `git diff --check` passed with exit 0; Git emitted only CRLF
conversion warnings. Nine short-board relative links were checked with
`Test-Path` relative to `docs/content-video-engine`; all resolved. A `docs_find`
retrieval attempt was made, but the existing docs-layer builder still fails at
`effects/cards/dock_kind.json` card 4 `does`; that unrelated builder issue is
tracked separately as `DOCS-BL-01` and was not changed here.

**Files changed in the split phase:** `BACKLOG.md`, new
`BACKLOG-HISTORY-2026-09.md`, this report, and this worktree's existing register
row. The 19 external citation files, generated docs layers, code, PRPs, rulings,
media, and other boards were not edited.
