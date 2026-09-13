# Operator memory (promoted from Claude)

These memories were Claude-only: they lived in the Claude project memory folder, so
Codex, Hermes and Gemini never saw what the operator had corrected. The operator's intent
(P54, A4) is that any agent inherits them.

- **Canonical copy.** This repo copy is the reviewed, canonical one. `MEMORY.md` is the index;
  every other file is one memory.
- **Prose with quotes.** Unlike `docs/agent-memory/explorer/` (anchors only - that rule is
  unchanged), these files are prose and carry the operator's words verbatim.
- **Who writes it.** The parent (Fable) only. Delegated roles read it; they do not edit it.
- **Refresh.** `python content/video_engine/scripts/sync_operator_memory.py --export`
  copies the Claude memory folder here, rewriting `[[slug]]` links as relative Markdown links
  (a slug with no file becomes `` `slug` (not yet written) ``). Extra files are reported, never
  deleted, unless `--prune` is passed. A file with a secret-looking string is not copied.
- **Drift.** `python content/video_engine/scripts/sync_operator_memory.py --check` exits 1 and
  lists each drifted, missing or extra file.
