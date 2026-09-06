---
name: retrieval-layers
description: How to find anything in this repo cheaply - docs_find first, the generated layers, windows not whole files, 'not found where I looked', never a backgrounded search. Preloaded by the read-only roles; load on demand elsewhere.
---

# Retrieval layers

Measured in `evals/RETRIEVAL-BENCHMARK-2026-09-05.md` (rounds 1-5).

- **Retrieval order — `python content/video_engine/scripts/docs_find.py "<term>"` first** (one compact line per hit across the layers, cheapest first; add `--layer manifest|index|topics|cites|gates|animation|craft` to focus, `--limit N` to widen), then `sed -n` the window it names. The raw `rg` per layer below is the fallback when you want the whole record (the layers are generated; `build_docs_layers.py --check` keeps them honest):
  1. *Do we have X / which doc holds it* → `rg -i "<x>" docs/DOCS-MANIFEST.jsonl` (one entry per document: purpose, what it defines, headings, key terms).
  2. *Where is the section* → `rg -i "<x>" docs/DOCS-INDEX.jsonl` (every heading, lead, label and body term → `path:line`), then `sed -n` a window.
  3. *Everything we hold about X across docs / what cites section Y* → `rg -i '"topic": "<x>' docs/DOCS-TOPICS.jsonl` and `rg '"ref": "<42§42.2|E38|G-j>"' docs/DOCS-CITATIONS.jsonl`.
  4. *A gate by id or phrase* → `rg -i "<id>" docs/GATES-REGISTRY.md`; *a formula, dial or law* → `docs/ANIMATION-REGISTRY.md` (status: implemented / tracked / retired / orphaned); *a writing device* → `docs/CRAFT-MAP.md`.
  SigMap (`python scripts/sigmap_context.py query`) is for code symbols only; the research bundle under `content/video_engine/sources/reference_analyses/` is inside the index.
- **Never background a search.** Every `rg` / `grep` / `find` runs to completion in the foreground with a bounded scope (`-g`, a root, `| head`); a scan left running past your answer is a second report the parent has to read (benchmark rounds 1-4: every straggler was this).
- Prefer `rg`, `ast-grep run --lang ... --pattern ...` and `sed -n a,bp` over reading whole files; never dump a file over 200 lines into your context when a 20-line window answers the question.
- Report **"not found in <the roots I searched>"** with the roots and the coverage limits named (what was time-boxed, what was not opened), never **"does not exist"**: the research bundle under `content/video_engine/sources/reference_analyses/` and `git log -S` are the two places a first pass misses. The parent verifies every negative claim.
- Your memory is WORKER SCRATCH, worktree-local and gitignored (`memory: local` -> `.claude/agent-memory-local/<role>/`): a map of where things live, one line per fact, **`path | heading or symbol | what`** (an anchor, never a line number; `rg -n` the anchor at query time), never a transcript. Read it first, add to it last. Paths are repo-relative. The DURABLE layer is `docs/agent-memory/<role>/` in the repo: read it too; never write it - propose a promotion in your report and the parent reviews it in (P2 memory contract, 2026-09-05).

