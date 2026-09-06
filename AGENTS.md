# AGENTS.md — Outreach Program / SEO Insights Platform

This file is the operating playbook for any agentic system (Hermes, Claude Code, Codex, OpenCode) working in this repo. It is the durable, always-loaded layer. Conditional workflows belong in skills, not here.

Read this file first, then read [`docs/AGENT_START_HERE.md`](docs/AGENT_START_HERE.md)
and its authoritative [`docs/agent-context/SKILL_ROUTER.md`](docs/agent-context/SKILL_ROUTER.md).
Load only the task route and PRP named there; do not preload the full docs tree.

---

## 1. Mission

Turn a pasted URL/domain into a **repeatable, evidence-backed SEO intelligence package** — not a one-off script run. The product is a `URL -> SEO Insight Run` engine with a stable data model, deterministic pipeline, repeatable scoring, and operator-facing artifacts.

Competitor intelligence, outbound automation, and generative content are **out of scope for v1**.

---

## 2–8. The SEO Insights Platform — moved to [`docs/AGENTS-SEO-PLATFORM.md`](docs/AGENTS-SEO-PLATFORM.md)

Architecture summary, the canonical `InsightRun`, the nine stages, the evidence-first definition of done, the verification commands, the artifact layout and the repo conventions live there unchanged. **Load it for any SEO-platform task, and whenever a doc cites its §2–§8** (the video-engine docs cite §5, the evidence-first definition of done, as universal). Moved 2026-09-05 to cut the always-loaded layer that every subagent dispatch re-pays. The rule that binds everywhere regardless: point to the artifact, not the claim.

---

## 9. Agent routing and durable execution

Use [`docs/runbooks/PRP_EXECUTION.md`](docs/runbooks/PRP_EXECUTION.md) for
complex, multi-slice, architectural, data-model, security, or release work.
Active plans live under `.claude/PRPs/plans/` as agent-neutral durable state.

- The parent task owns architecture, integration, protected actions, and the
  final completion claim.
- `speedster` handles exact deterministic microtasks only.
- `junior_developer` handles bounded limited implementation, scoped fixes,
  explicit line changes, and small reads/writes.
- `implementation_luna` handles bounded moderate implementation with tests.
- `architect_sol` researches and drafts implementation-ready PRPs.
- `explorer` performs read-only repository tracing and evidence gathering.
- `docs_researcher` performs read-only primary-documentation verification.
- `reviewer` performs read-only correctness, security, and regression review.
- `release_steward` performs reviewed Git mechanics only; push still requires
  current explicit user authorization.
- The eight roles are real agent types on both sides: `.codex/agents/*.toml`
  and `.claude/agents/*.md`. **Model policy (2026-09-05): the parent session
  is Fable and spends its tokens on judgement only; every delegated role runs
  on Opus 5 (`speedster` on Sonnet 5 - not Haiku: the overhead is the cost, a wrong edit is dearer).** Offload recall (`explorer`), review
  (`reviewer`), docs checks (`docs_researcher`), bounded implementation and
  git mechanics (`release_steward`) instead of doing them in the parent.
- Three harnesses share this checkout (Gemini research, Codex/Astra→Luna
  implementation, Claude/Fable→Opus doctrine and gates): lane write sets in
  `docs/runbooks/PRP_EXECUTION.md`; research intake in `GEMINI.md`.
- Keep write sets disjoint and review delegated diffs before integration.
- Subagent summaries are not proof. Require artifact paths, run IDs, diffs, or
  command output.
- Keep task state in the PRP, not in transcripts or this file.

---

## 10. Local code-navigation workflow

Use the portable wrapper from the repository root when a named symbol, service, or architecture path needs ranked evidence:

```bash
python scripts/sigmap_context.py build
python scripts/sigmap_context.py query "sitemap discovery" --top 5
python scripts/sigmap_context.py evidence "CrawlDiscoveryService" --markdown
```

Every wrapper command regenerates the local index first with `--no-track`. Its configuration writes only the gitignored `.github/copilot-instructions.md`; it does not modify `AGENTS.md` or `CLAUDE.md`, register MCP clients, or invoke Codex/Claude adapters.

Route questions to the smallest suitable tool:

- **SigMap**: declared symbols, ranked architecture discovery, and evidence packs.
- **ast-grep**: structural patterns and exact call-site sweeps. Always set `--lang`, use a narrow pattern, and scope it to repo-relative paths; one-shot `run` needs no `sgconfig.yml`, while reusable configured rules use `scan`.
- **Text search** (`git grep` or `search_files`): literals, configuration keys, SQL, docs, and test descriptions.
- **SQZ**: compress noisy command output or logs only after saving the original evidence. Feed the SAVED output on stdin: `sqz compress --mode safe --verify --no-cache --cmd <producer-name> < .context/<file>` (`--cmd` is a label for `sqz stats`, not a runner - it does not execute the producer; verified 2026-09-02, sqz 1.3.0). Do not compress hashes, exact test verdicts, security evidence, or small outputs (a 30-line gate report compressed 2%), and never use SQZ as a search or correctness tool.

Windows path rule: set the command/tool workdir to the exact repository root and pass `.` or repo-relative paths. The native Windows `rg` used by `search_files` does not accept MSYS-style absolute paths such as `/c/Users/...`; if an absolute-path search fails, retry from the exact workdir with a relative path before concluding that nothing matched.

Bound a structural sweep and preserve its raw output before optional compression:

```bash
ast-grep run --lang python --pattern 'class $C: $$$BODY' src/services --json=stream > .context/ast-grep-classes.jsonl
sqz compress --mode safe --verify --no-cache --cmd ast-grep < .context/ast-grep-classes.jsonl
```

---

## Content video engine (second workstream)

This repo also hosts a faceless YouTube production operation (three
channels: Money Physics, Building Money, Martial Matters). It is a
separate workstream from the SEO platform above and has its own doctrine.

**Any agent doing script, visual, evidence, or channel work loads these
two files first — they are model-agnostic and are the source of truth:**

- [`docs/portable/DOCTRINE-CORE.md`](docs/portable/DOCTRINE-CORE.md) —
  ~10k chars, always loaded: channels, narrator, retention clock,
  six-phase architecture, sentence gates, packaging, production
  standards, never-list. Sized to paste into any system-instruction box.
- [`docs/portable/OPERATOR-RULINGS.md`](docs/portable/OPERATOR-RULINGS.md)
  — the standing corrections ledger; each ruling carries the reason it
  was made, because the reason is what generalizes.

- [`docs/portable/VOICE-PACK.md`](docs/portable/VOICE-PACK.md) — loaded
  before writing any narration, title, or description. Voice transfers by
  exemplar, not description: a rejected/accepted hook pair, the five
  hardest lines from an approved script, and the ear-judgments converted
  to text-checkable rules.

Task routing into the deeper doctrine, plus the work-order interop
contract, is in [`GEMINI.md`](GEMINI.md) — that routing table applies to
every agent, not just Google-side ones.

**The assembly process itself is one page:
[`docs/content-video-engine/PIPELINE.md`](docs/content-video-engine/PIPELINE.md)
— the eight stages (write → strength loop → lint → audit → record → word
timeline → shot table → render), what owns each, what consumes what, and
the capability index it opens with. Read it before building anything;
the renderer, the player and the gates already exist. Enumerate before
you grep. Lane capabilities are stated from the docs and the template,
never from memory - cite the file (CHECK-RESPONSIBILITIES R9).**

**Three spine documents sit behind that table. Know they exist before
doing script, review, or motion work — they were unrouted until
2026-09-02 and lived on one branch only:**

- [`docs/content-video-engine/patterns/FULL-VIDEO-MAP.md`](docs/content-video-engine/patterns/FULL-VIDEO-MAP.md)
  — **the script spine.** The classical six-phase architecture (Truby /
  McKee / Snyder / Glass / ring composition — the integral) fused with the
  platform retention micro-rules (the differentials) at every 15–90s
  interval. The phase guides `P1–P6` and the strength loop derive from it;
  `patterns/KNOWLEDGE-GRAPH.md` is the same graph laid out by relation.
- [`docs/content-video-engine/patterns/CHECK-RESPONSIBILITIES.md`](docs/content-video-engine/patterns/CHECK-RESPONSIBILITIES.md)
  — **who checks what.** Three verdict kinds (mechanical / declared /
  JUDGE) decide whether a tool or the runtime agent owns a verdict; §2
  tables the four checkers (`lint_script_pattern.py`,
  `audit_script_doctrine.py`, `gate_opening_structure.py`,
  `enumerate_strength_screens.py`); §3 names everything the agent must
  verdict by hand; §5 fixes the report format. A tool's verdict is final;
  a declared tag is a claim the agent verifies; a report missing a block is
  not a review.
- [`docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md`](docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md)
  — **motion and evidence choreography, the production bar for every
  channel.** Part 3 is the linked-evidence choreography (the chain is the
  transition), Part 8 the scene-evidence lane that ships, Part 9 the
  operator corrections, §9.15 the cross-reveal wipe and caption safe zone.
  Doc 16 (editorial motion system) is partially superseded by it and doc 15
  (living-scene language) is record only — where they disagree on motion,
  29 wins. The renderer is `samples/scene-evidence-player.template.html`;
  do not write another.

Three rules bind agents generating assets here:

1. A dispatched `WORK-ORDER.md` is **frozen**. Corrections open a new
   claim; never patch an order a running agent already holds.
2. Output stays in **review quarantine** until the operator approves a
   contact sheet. Free generation does not remove the review step.
3. `approved` is set by the operator, never by product code, and figures
   are never fabricated — unverified claims go under SOURCES-TO-VERIFY.
