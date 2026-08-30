# CAPABILITIES — what is already built

**Check this file before building anything.** Three asset classes were
rediscovered in one session (2026-08-29) — the curtain-era wipe grammar, the
typewriter record document, the live chart draw — each rebuilt or nearly
rebuilt because nothing indexed what existed. The plate library indexes
plates; the choreography ledger indexes motion events; this file indexes
**capabilities** — renderers, engines, gates, prototypes.

Format: what it does · where it lives · state · proof. Update it in the same
commit that adds or retires a capability. A capability that is not in this
file will be rebuilt by someone who doesn't know it exists.

## Rendering & playback

| Capability | Where | State | Proof |
|---|---|---|---|
| **Scene-evidence player** — the review renderer: cross-reveal wipe with carried light, coalesced docks, snap-to-boundary, dock-owned sides, interval wash, finance geometry (864/1056), one-baseline spring pills, text-tier palette | `docs/content-video-engine/samples/scene-evidence-player.template.html` | LIVE — the lane | Steel and Paper build F |
| **Record-document species** — typewriter + per-word highlighter, stroke synced to the NARRATOR's word timings | template (`drawRecord`) + prototype `steel-and-paper/evidence/prototypes/record-document-motion.html` | LIVE (Karp wired); leases/macdonald await payloads | 3:10 in build F |
| **Live-chart species** — stroke-dashoffset line draw from a `.series.json` sidecar; star series lands last; labels de-overlap | template (`drawChart`) + sidecar emit in `build_evidence_documents.py` | LIVE (divergence wired); other charts await sidecars | 0:17–0:24 in build F |
| **Narration-keyed chart draw** — DRAW_KEYS bound to word timings ("the crash lands on the words") | prototype `evidence/prototypes/data-document-motion.html` | BUILT, unwired — binds after re-record | prototype replays |
| **Kinetic + quiet captions** — word-punch groups at canonical timings; quiet mode under any docked evidence | template + `caption-pages.json` from the words sidecar | LIVE | doc 29 Part 5 |
| **Choreography ledger + gates** — every enter/exit/side/how-it-leaves, gated per slot; FAIL blocks the build | `content/video_engine/scripts/emit_choreography.py` → `build-f/CHOREOGRAPHY.md` | LIVE — constants mirror the template; change together | caught tnx re-landing on first run |
| **Whiteboard reveal engine** — serpentine SVG mask + hand follower, pose set with per-pose nib calibration | git history `7880c01`, `1e6612f`; poses `hyperframes/assets/hands/` + `nib-calibration.v1.json` | RETIRED from this lane (doc 29 8.17) — earns its place when artwork is drawn, not sourced | doc 29 8.10–8.16 |
| **Remotion Production Console** — local timeline/canvas editor + Python bridge (`127.0.0.1:4317`): scrub/zoom/drag/trim, hash-bound immutable revisions, recompiles without touching narration or evidence approvals; semantic-evidence binding tests | `content/video_engine/production_console/` + `configs/production_console_snapshot*.schema.json` (merged from p31, 2026-08-29) | BUILT — the doc 29 §9.3 production route | P29/P31 gate screenshots in `.claude/PRPs/evidence/` |
| **Remotion composition registry** — single source of truth for editor compositions (Editorial, Documentary, motion variants, finance proofs, production evidence/timeline, 3D prototypes) | `content/video_engine/editor/src/compositions.ts` | LIVE — register here, never in Root.tsx | typecheck + vitest |
| **Editor fixtures** — editorial-motion two-shot with render harness (`render.mjs`), canonical audio fixture | `content/video_engine/editor/fixtures/` (merged from p16) | BUILT | `npm run render:editorial-motion-fixture` |
| **remotion-ui registry** (external, MIT) — ~200 copy-in `.tsx` components: captions, data/live metrics, SVG draw-on paths, TransitionSeries transitions, motion primitives; MCP server (`npx remotion-ui-mcp`) exposes list/search/detail/install to agents | github.com/riaz37/remotion-ui · remotionui.com/docs/components/browse | EVALUATE on the Remotion port — copy-in means doc 29 numbers overwrite defaults; every component takes the doctrine pass before shipping a frame | operator-sourced 2026-08-30 |
| **Hyperframes** — production vector animation (alpha overlays, compositions); Remotion port path | skills in codex worktree `f10b/.agents/skills/hyperframes*`, assets `content/video_engine/review/hyperframes_assets` | BUILT, not in the review loop — the doc 29 §9.3 production route | pinned CLI renders alpha natively (doc 29 Part 7) |

## Evidence & assets

**Martial Matters episode 1** (merged from p16, 2026-08-29): 192 asset files
(1080p plates), recorded narration + word timings
(`projects/martial-matters/.../transcript/narration.words.json`), the
Marshall Monday editing handoff. The third channel's pilot — indexed in the
plate library under channel `martial-matters` (2026-08-29), semantics from
the word-timed cue ledger, state `candidate` until an approval manifest is
read.


| Capability | Where | State | Proof |
|---|---|---|---|
| **Plate library** — 326 plates indexed by SEMANTIC across all worktrees and CHANNEL-AWARE (money-physics 134 / martial-matters 192); channels are identity walls — the resolver refuses cross-channel plates; status from manifests, never paths | `content/video_engine/scripts/build_plate_library.py` → `sources/PLATE-LIBRARY.json` | LIVE — rebuild after any plate wave | resolver falls through to it |
| **Chart builders** — real-data charts (yfinance/FRED), verbatim end labels, month/year axes, series sidecars | `steel-and-paper/evidence/build_evidence_documents.py` (+ railway, HBM builders) | LIVE | ev-divergence-v1 |
| **Live HTML evidence sources** — karp/leases/macdonald records, instrument-memory, mechanism-ladder, three-manias | `steel-and-paper/evidence/*.html` | BUILT — PNGs are flattened renders of these | files on disk |
| **Teacher-stamped catalog** — 86 production slides keyed `image_id` → `extracted_path` | `sources/decks/teacher-stamped-production-visuals/` + manifest (MAIN checkout) | LIVE | episode-build skill §5 |
| **Two-tier palette** — graphic tier for lines/fills, lifted text tier for numerals on dark pills | template `:root` + BUILD-PIPELINE.md | LIVE — never graphic-tier text on dark | contrast 5.7–7.4:1 measured |

## Script & voice

| Capability | Where | State | Proof |
|---|---|---|---|
| **Strength loop** — multi-scale fixpoint (L0–L6 + X1–X5), rewrite budget, oscillation escalation | `patterns/STRENGTH-LOOP.md` + script-writer skill | LIVE | Script F |
| **Doctrine audit + pattern lint** — timed gates from text via dual rate estimators (16.29 c/s, 170.9 wpm) | `scripts/audit_script_doctrine.py`, `lint_script_pattern.py`, `kit_spec.py` | LIVE | |
| **Recorder preflight** — 16 gates: split-on-pause, tag cap, paragraph density, stacked pauses, credits-for-both-parts | `scripts/record_chained_take.py` | LIVE — both new gates FAIL on the take that shipped bad | doc 37 |
| **Pause compilation** — marks → break tags, backticks consumed, dirty-tag guard RAISES | `src/services/audio_synth.py` `compile_pause_marks` | LIVE | the 0:08 artifact class is unshippable |

## Reference builds (locked)

| Reference | Where | Governs |
|---|---|---|
| **current-bubble-five-minute-v4** | `samples/current-bubble-five-minute-v4.timeline.json` (+ rendered build) | THE motion gold standard (doc 29 §9.16) — side-by-side before any motion change ships |
| **Gemini showcases** | `samples/gemini-decoupled-evidence-showcase.html`, `gemini-scene-evidence-pipeline-showcase.html` | ancestor artifacts — where doctrine CAME from; a reviewed refinement outranks them |

## The recall rule

1. `ls` and read the index before searching (PIPELINE.md, this file, PLATE-LIBRARY, CHOREOGRAPHY).
2. When a doc cites a source artifact, the audit reads the artifact.
3. A capability added or retired updates this file **in the same commit**.
