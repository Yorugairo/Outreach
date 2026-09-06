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

## Content video engine (second workstream) — moved to [`docs/AGENTS-VIDEO-ENGINE.md`](docs/AGENTS-VIDEO-ENGINE.md)

This repo also hosts a faceless YouTube production operation (Money Physics, Building Money, Martial Matters). **Any agent doing script, visual, evidence or channel work loads that file first**; it names the two portable files (`docs/portable/DOCTRINE-CORE.md`, `docs/portable/OPERATOR-RULINGS.md`), the pipeline page, the three spine documents and the three binding rules (a dispatched work order is frozen; output stays quarantined until the operator approves; `approved` is the operator's and figures are never fabricated). Retrieval for any of it: `python content/video_engine/scripts/docs_find.py "<term>"`. Moved 2026-09-05 to cut the layer every dispatch re-pays.
