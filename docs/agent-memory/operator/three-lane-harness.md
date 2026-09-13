---
name: three-lane-harness
description: "2026-09-05: three harnesses share the Outreach checkout - Gemini/Antigravity = research + Flow (context sponge, reduces once), Codex/Astra->Luna = tools + bounded implementation, Claude/Fable->Opus = doctrine/gates/evidence/review; the reduction pipeline is raw report -> catalog -> section index (DOCS-INDEX) -> reviewed memory; Astra's P2 plan (otn/shared) is the future order/result contract"
metadata:
  type: project
---

**Operator, 2026-09-05 (evening):** Antigravity is driven by CLI (`agentapi new-conversation --model=pro --profile=...`); Gemini is the research agent / context sponge (flat subscription, huge context) that drives Google Flow, does web research and adds it to the index; Astra (OpenAI) drives Luna agents to develop and search; Fable drives Opus and Sonnet. "One provider-neutral harness, developed in otn/shared" - Astra's PRP `C:/dev/one-network-worktrees/otn/shared/.claude/PRPs/plans/subscription-agent-orchestration.plan.md` (P2): roles table, versioned JSON execution orders with hashes and approval records, three memory layers (repo `docs/agent-memory/` reviewed; worktree-local session state; small worker bootstrap), research ingestion (raw reports authoritative, deterministic publish, section spans with hashes), a 12-case held-out retrieval eval. Gemini's protocol: `docs/research/CATALOG.json` + `INDEX.md` (document-level, `scripts/index-research-catalog.mjs`), four trades-repo profiles, proof line `[Metric | Value | Authority | URL | Verified date]`, `[UNVERIFIED]` tags, golden rule: never web-search a fact already in the repo.

**What this repo did (commit 8d5c502):** `GEMINI.md` "Research intake" (where reports land, headings name the concept, proof line, NOT FOUND block, reports are data, `build_docs_index.py --write` after writing); runbook "Lane write sets" (Gemini: docs/research + Flow batches; Codex: tools + ordered slices; Claude: doctrine/gates/evidence/.claude; shared files one row at a time, own-author commits, never another lane's uncommitted files); `docs/runbooks/HANDOFF-ASTRA-GEMINI-2026-09-05.md` = the paste-ready note: seed P2 T2 from build_docs_index.py, reconcile native `memory:` as worker scratch + reviewed promotion, three lines for the Gemini protocol, name the pipeline once.

**How to apply:** commission research (do not do it inline); rg DOCS-INDEX first; Gemini for this repo still needs the operator to add the repo root to `~/.gemini/trustedFolders.json` / `projects.json` and a `video-researcher` profile (not done). Model ids for Astra/Luna are the operator's to set in `.codex/agents/*.toml` - never guess them. See [fable-parent-opus-roles](fable-parent-opus-roles.md), [our-artifacts-beat-outside-advice](our-artifacts-beat-outside-advice.md).

**Astra's review (same evening, accepted):** indexer roots configurable (luna slice); agent memory = `memory: local` worker scratch (worktree-local, gitignored) + `docs/agent-memory/<role>/` durable layer written only by the parent after review; NOT FOUND names roots + coverage; benchmark labelled (Fable-sub vs Opus-sub, different prompts; inline baseline rough; persistence unmeasured; false-negative case is a dev/regression case). Direct lane-to-lane comms = shared artifact + tiny CLI request returning deltas. **Claude CLI on this machine: installed (2.1.259) and logged in as sniperownage (Max); `claude -p` works from the repo root** - an earlier 'Not logged in' was a cwd/env artefact; a lane seeing the old account has a different HOME.

**The bridge, measured 2026-09-06:** Claude -> Gemini = `~/.gemini/antigravity-cli/bin/agentapi.bat new-conversation --model=pro "<order>"` with env ANTIGRAVITY_LS_ADDRESS=127.0.0.1:<2nd language_server port>, ANTIGRAVITY_CSRF_TOKEN (from language_server.exe's --csrf_token; never print), ANTIGRAVITY_PROJECT_ID=<repo PATH, not the name>; progress in ~/.gemini/antigravity/brain/<id>/.system_generated/logs/transcript.jsonl; nobody polls docs/runbooks for orders - an order must be SENT. Astra -> Claude already runs as headless `claude -p` review packets (agent-bridge-run-* sessions: one JSON packet, one structured reply). First Gemini order: 7aaa9146 (the profile work order). Mechanics in GEMINI.md 'Commissioning Gemini from the Claude lane'.

**Gemini model tier (operator, 2026-09-06):** send bridge orders with `--model flash` (the CLI's tiers are flash_lite | flash | pro); the current flash (3.8) is stronger than pro (3.1). bridge_send.py defaults to flash. The first live order (Wealth Logic cuts, conversation 12655d39) went out on pro before this ruling.

**2026-09-09/10, Gemini in the timeline lane went poorly:** it tried an "Option B" chart dock on Tokyo (ev-japan-selling series +
dock-k), reverted itself to 983f5f5 (verified: only the authored SHOT-TABLE differed, since committed), and its plain rebuild of
the TARIFF short used the default `still` arm - the watched player served the charcoal arm until I rebuilt `sig` (now the
default; fix c-commit 2026-09-10). Its Bravos watch report (`sources/reference_analyses/bravos-china-just-triggered-a-new-world-order/`)
has the right SHAPE (our 6-phase template, CPM, WPM) but its numbers are tool artifacts: shot boundaries on a fixed 5.7 s sampler
(durations all multiples of 5.7), every shot `unclassified`, phase word counts double-count overlapping auto-caption windows
(4,530 vs 3,543). Gemini's own close: it steps back to research intake and evidence extraction. Treat a Gemini timeline change as
a candidate to be rebuilt from the shot table, never as the build of record.

