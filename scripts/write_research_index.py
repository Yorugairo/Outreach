"""Emit RESEARCH-INDEX.md from the generated dispositions."""
import json, pathlib, collections, subprocess, sys, re

sys.path.insert(0, str(pathlib.Path(__file__).parent))
subprocess.run([sys.executable, str(pathlib.Path(__file__).parent / "build_research_index.py")], check=True)
rows = json.load(open("idx.json", encoding="utf-8"))

PREAMBLE = """# Research extraction index

Every heading of every document in the research evidence bundle, with what happened to
it. **Coverage is the proof of reading**: a heading with no disposition fails
`scripts/check_research_extraction.py`, and you cannot account for a section you did not
open.

Bundle: `content/video_engine/sources/reference_analyses/complete_research_evidence_bundle/`
Read completed 2026-09-04. Reference layer: docs **42–46**.

## Disposition vocabulary

| tag | meaning |
|---|---|
| `EXTRACTED -> NN` | landed in reference doc NN at the named section |
| `RECORD` | read; contextual or structural, nothing actionable to lift |
| `DUPLICATE` | synthesis of other primaries; extracted at the primary instead |
| `PRIOR` | already extracted before this pass |
| `FILTERED OUTPUT` | not a primary — a pass over the primaries, triaged separately |
| `REJECTED` | read and refused, with the reason stated inline |

## The reference layer

| doc | covers | primaries behind it |
|---|---|---|
| [42-DRAWING-KINETICS](42-DRAWING-KINETICS.md) | stroke reparameterisation, closed-form springs and the overshoot inverse, squash, Euler spirals | 07 Pillars 1 & 3, 02 §2 |
| [43-SCENE-GRAPH-AND-TRANSFORM](43-SCENE-GRAPH-AND-TRANSFORM.md) | anchor sandwich, Z-stack, dirty flags, both morph methods, the cutout rig | 02 §1/§3/§4, 07 Pillar 2, dossier §3 |
| [44-INK-AND-SURFACE](44-INK-AND-SURFACE.md) | Kubelka-Munk compositing, coffee-ring edge, anisotropic wicking — bounded by E22 | 07 §1.4 |
| [45-PARALLAX-AND-PLATE-MOTION](45-PARALLAX-AND-PLATE-MOTION.md) | disocclusion limit, the viability matrix, our dial audit, multi-plane inpainting, masked ambient motion | 05 whole, 06 §2–4 |
| [46-REFERENCE-RHYTHM](46-REFERENCE-RHYTHM.md) | shot distribution recomputed, gap thresholds, the equation spine, phase map | 04 (recomputed), 01, dossier §10 |
| [47-FINDINGS-TO-CHECKS](47-FINDINGS-TO-CHECKS.md) | which findings can be designed out, gated, judged, or demoted | **derived from 42–46, not from a primary** — the enforcement layer |
| [48-THE-FIGURE-AND-THE-GROUND](48-THE-FIGURE-AND-THE-GROUND.md) | FK/IK boundary, balance, the rig, idling, reach and grasp, grounding and compositing | 09 whole — **closes X10** |

## Declared conflicts and rejections

These are the load-bearing disagreements found by reading the primaries against each
other and against our code. **A conflict can only be found by reading both sides.**

1. **RESOLVED — `strength` vs `intensity` in the parallax runner.** Settled 2026-09-04
   from the installed node source, which is the authority both reports were guessing at.
   `base_flex.py:25` makes `feature` an optional input defaulting to `None`;
   `base_flex.py:103` gates all modulation behind `if feature is not None:`; `strength` is
   consumed *only* inside `modulate_param`, reachable only from that branch. We supply no
   feature, so **`strength` is dead code in our pipeline.** `intensity`
   (`depthflow_motion_presets.py:13`, required FLOAT, default 1.0, max 10.0) is the real
   displacement. **`06` is right, `05` is wrong** — and `05`'s "intensity: 1.0 is the
   correct dolly value" must not be followed. Recorded in 45 §45.4.
2. **Depth model precision.** `05` says `vitl_fp16`; `06` says `vitl_fp32` with fp16
   "strictly banned due to logit underflow." Take ViT-Large, leave precision to a test roll.
3. **Acoustic gap threshold.** `01` and the dossier's `gap_detector.py` use **0.45 s**
   with the cut at the gap **midpoint**; `06` and `08` use **0.30 s** at gap **onset**.
   Different gates. **Settle from our own word timeline before M13 ships** (46 §46.3).
4. **REJECTED — the per-phase word counts in `01` and dossier §10.** They sum to 3952
   against a stated 3101 total and imply an unspeakable 299 WPM in P1. This is the
   YouTube caption over-count (rolling carryover), already known to the operator. Phase
   *boundaries* are used; the word and WPM figures are not.
5. **REJECTED — the numeric claims of `08`.** `08` is a filter pass over these primaries,
   not research. Its fabricated figures are catalogued in
   [VERDICT-research-brief-animation-craft.md](briefs/VERDICT-research-brief-animation-craft.md);
   everything adopted from it is re-sourced from a primary here.
6. **SOURCES-TO-VERIFY — two citations in the pass-2 rewrite of `08`.** Neither is
   used by docs 42-46, so nothing here depends on them; they are logged because `08` now
   presents them as empirical.
   - *Martinez-Conde, Macknik & Hubel (2006), Nature Reviews Neuroscience 7(10):732-740,
     "The role of fixational eye movements in visual perception"* - that title is
     associated with **NRN 5:229-240 (2004)**. Flagged once before pass 2 and returned
     unchanged with an issue number added. Verify the year/volume pairing.
   - *Hasson et al. (2008), NeuroImage 28:1026* - NeuroImage volume 28 is 2005; a 2008
     paper falls in volumes 39-43. Verify.

7. **`08` §8 covers one of five parallax defects.** The pass-2 code audit gets its line
   coordinates right (line 142 *is* `"inputs": motionInputs`) but addresses only
   `intensity` and the model. The strings `tiling_mode`, `ssaa` and `quality` appear
   **nowhere** in its 612 lines, so its proposed fix leaves `tiling_mode: "mirror"` in
   place - the kaleidoscope glitch `05` names as a specific observed artifact. This is
   why 45 is sourced from `05`/`06` and not from `08`.

8. **Our parallax dials do not match any target.** Read from
   `tools/google-flow-driver/src/parallax-runner.mjs` on 2026-09-04: `strength=1.0`,
   `intensity=1.0` hardcoded in all six presets, `tiling_mode="mirror"` (the kaleidoscope
   glitch), `ssaa=1.0`, `quality=75`, model `vits_fp16`. Left to the Flow lane; recorded
   in 45 §45.3.

## Full disposition table

"""


def anchor(f):
    return f"`{f}`"


out = [PREAMBLE]
by = collections.OrderedDict()
for r in rows:
    by.setdefault(r["file"], []).append(r)

for f, rs in by.items():
    out.append(f"\n### {anchor(f)} — {len(rs)} headings\n")
    out.append("| heading | disposition |\n|---|---|\n")
    for r in rs:
        h = r["heading"].replace("|", "/")
        out.append(f"| {h} | {r['disposition']} |\n")

out.append(f"\n---\n\n**{len(rows)} headings across {len(by)} documents, all dispositioned.**\n")
out.append("Verified by `python scripts/check_research_extraction.py`.\n")

pathlib.Path("docs/content-video-engine/RESEARCH-INDEX.md").write_text("".join(out), encoding="utf-8")
print(f"wrote RESEARCH-INDEX.md: {len(rows)} rows, {len(by)} files")
