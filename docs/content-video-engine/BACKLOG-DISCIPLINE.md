# Video-engine backlog discipline

Status: current. Last reviewed 2026-09-23.

## Board contract

- `BACKLOG.md` is the canonical active queue. Its opening tables organize work
  by execution context: running PRP, human review, triggered backlog, and
  bounded experiments.
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
the historical section; all 274 R26 source-row headers are preserved. Nothing
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
