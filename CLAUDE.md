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
- **Delegate, don't do** → the eight roles in `.claude/agents/` run on Opus 5
  (`speedster` Haiku); the Fable parent keeps judgement, integration and the
  operator. Recall = `explorer`, review = `reviewer`, git = `release_steward`.
  Policy: `docs/runbooks/PRP_EXECUTION.md` "Dispatch mapping".
