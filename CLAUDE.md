# CLAUDE.md

Claude Code reads this file; Codex and Hermes read `AGENTS.md`; Gemini reads
`GEMINI.md`. All three carry the same playbook, so this file imports it
rather than restating it.

@AGENTS.md

## Fast routes (the ones agents kept re-discovering)

- **Assemble or build an episode** → `docs/content-video-engine/PIPELINE.md`
  (stages 1–8: write → loop → lint → audit → record → timeline → shot table
  → render) and the capability index it opens with. Enumerate before you
  grep: the renderer, the player, and the gates already exist.
- **Write or review a script** → `docs/content-video-engine/patterns/SCRIPT-PATTERN-KIT.md`;
  spine: `patterns/FULL-VIDEO-MAP.md`; who checks what:
  `patterns/CHECK-RESPONSIBILITIES.md`.
- **Motion, evidence, choreography** → `docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md`
  (Parts 3, 8, 9; §9.15).
- **Voice** → `docs/portable/VOICE-PACK.md`, docs 33 + 36. **Rulings** →
  `docs/portable/OPERATOR-RULINGS.md` (override everything else).
- **Do we have X? Where is it? Everything about it?** →
  `python content/video_engine/scripts/docs_find.py "<term>"` first (one compact line per
  hit, cheapest layer first, names the window to open); the raw layers as fallback, one `rg` each:
  `docs/DOCS-MANIFEST.jsonl` (per document: purpose, defines, headings),
  `docs/DOCS-INDEX.jsonl` (per section → `path:line`), `docs/DOCS-TOPICS.jsonl` +
  `docs/DOCS-CITATIONS.jsonl` (across docs; who cites what), `docs/GATES-REGISTRY.md`
  (every gate by id), `docs/ANIMATION-REGISTRY.md` (every formula, dial, law with
  status), `docs/CRAFT-MAP.md` (every writing device). Never say "we don't have it"
  before the manifest grep. Regenerate all: `build_docs_layers.py --write`.
- **Delegate, don't do** → the eight roles in `.claude/agents/` run on Opus 5
  (`speedster` Sonnet); the Fable parent keeps judgement, integration and the
  operator. Recall = `explorer`, review = `reviewer`, git = `release_steward`.
  Policy: `docs/runbooks/PRP_EXECUTION.md` "Dispatch mapping".
