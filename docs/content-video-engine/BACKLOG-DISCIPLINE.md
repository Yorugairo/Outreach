# Video-engine backlog discipline

Status: current. Last reviewed 2026-09-23.

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
