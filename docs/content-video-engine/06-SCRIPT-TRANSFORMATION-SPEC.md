# Script Transformation Spec — Essay/Corpus → Beat Sheet → Storyboard

> **STATUS: RECORD.** A point-in-time research note, review, or planning document. Not maintained, and not current doctrine — read it for how a decision was reached, not for what to do now. Live doctrine is indexed in [README.md](README.md).

> **History V4 override:** documentary transformation consumes an
> operator-approved `research_packet.v1`; it does not infer facts from essays,
> consultant material, reference videos, or visual assets.

## Evidence-constrained documentary transformation

For a `history_episode.v1`, every narration sentence carries one or more approved
claim IDs. Transformation may shorten, order, and qualify those claims. It may not
invent chronology, causation, motive, lineage, quotation, or certainty.

Direct quotations require an approved exact-text claim and a valid locator.
Contested claims require two independent citations and explicit qualifying
language. A visual reconstruction never adds factual detail: narration and
captions remain bounded by the claim matrix, while the image is labeled
`Illustration` or `Reconstruction`.

The documentary beat sheet uses
[`10-HISTORY-DOCUMENTARY-EDITORIAL-SPEC.md`](10-HISTORY-DOCUMENTARY-EDITORIAL-SPEC.md).
Its first-pass compiler is deterministic and refuses unapproved claims. An LLM may
later propose phrasing only if the same claim-boundary guard proves every sentence.

*Date: 2026-07-28 · Implements the operator's "Script Transformation Instructions" + "3 Golden Rules" as an enforceable spec · Enforced by: `storyboard_guard.py` (machine checks) + Gate A rubric (human checks).*

This is the editorial quality system. Rendering is deterministic; **retention is won or lost
here.** The transformer (LLM-assisted for essays, deterministic-floor for corpus techniques) turns
source content into a beat sheet, which `storyboard_build` compiles into the v2 storyboard.

---

## 0. Angle selection precedes transformation

The transformer does not decide what the channel believes. Before beat generation, the operator
may supply an angle brief derived from outlier/trend research:

1. **Pattern:** what question, tension, or format outperformed the reference channel's baseline?
2. **Inversion:** what original counter-premise can this project's fact layer actually prove?
3. **Skill stack:** which two defensible capabilities make the treatment hard to copy?
4. **Human thesis:** the operator's one-sentence point of view and why it serves this audience.

AI may organize references and propose candidates. It may not copy a title/premise, treat raw
views as evidence, manufacture a contradiction, or select the final thesis. Reference URL,
observed pattern, and operator decision remain in the source/job evidence; they are not written
into the immutable storyboard unless a later contract version explicitly adds them. Autonomous
reference scraping is P1 work, not a P0 dependency.

## 1. Length + pacing math (140 WPM basis)

| Output | Words | Runtime | Scenes (typ.) |
|---|---|---|---|
| Long-form (YouTube) | 600–900 | ~4:20–6:30 | 8–14 |
| Short / Reel | 90–130 | 40–55s | 2–4 (subset w/ own hook) |
| Source essay | 1,500–2,500 | — | compression ratio ≈ 3:1 |

`timing.target_s = word_count / (wpm_target / 60)`. The guard rejects storyboards whose summed
targets miss the format budget by >15% — fix the script, don't hope the TTS lands differently.

## 2. Pacing hierarchy (reconciling the 3–5s / 15–20s / 20–30s numbers)

The operator's sources give three cadence numbers; they're different layers, not contradictions:

| Layer | Budget | What changes | Enforced via |
|---|---|---|---|
| **Micro** | every ≤6s landscape / ≤3s vertical | *something* on screen moves: pose, label, camera, color | `pacing.visual_change_max_s` + `shorts_visual_change_max_s`; beats density check |
| **Interrupt** | every 15–30s | deliberate pattern break: comedic stick-figure reaction, diagram flip, scene change | `pacing.pattern_interrupt_max_s`; ≥1 interrupt-tagged beat per budget window |
| **Act** | every ~60–90s | narrative gear shift (new question, new lever, new location) | act structure check |

## 3. Conflict-loop arc (mapped to `scene.act`)

Linear summary (hook → explanation → conclusion) retains worse than a **looped conflict arc**:
hook → rising action → conflict → comeback → payoff. The transformer must surface a real central
conflict or misconception by the first third — never manufactured drama, but the tension the
source already contains (samurai punching iron armor; "just yank the arm out"; the fund that
couldn't lose money until it did).

- **`hook` (first scene, ≤12s).** Cold open — no logo, no "welcome back", no throat-clearing.
  Open on the most visual claim or the punchline-first ("This is the first submission you'll
  ever learn — and it still finishes black belts"). The hook is written LAST, after the payoff
  is known.
- **`develop` (1+ scenes).** One idea per scene; each scene must *earn* the next with an open
  loop ("but armor changes everything…"). For corpus techniques: transcript steps, reworded but
  never invented (provenance-checked, same rule as `llm_guard.guard_technique`).
- **`conflict` (≥1 scene for runs >90s).** The misconception, obstacle, or reversal ("your
  instinct is to pull the arm free — that's the finish"). Sourced, never invented; claims rules
  apply to conflicts too.
- **`comeback`.** The turn that resolves the conflict and sets up the payoff. Comeback without
  conflict is filler; conflict without comeback is clickbait — the guard checks the pairing.
- **`payoff` (1+ scenes).** The information-gain moment — the lever diagram, the map spread, the
  blowup mechanism. If the payoff could appear in any generic explainer, the video is rejected
  at Gate A (Golden Rule 2).
- **`cta` (last scene, one only).** Spoken + on-screen, single destination, UTM-tagged.
  Double-CTAs and mid-roll CTAs are banned — they buy clicks with retention.

### Flow rules (anti-random-cut)

Automated video dies by disjointed jumps. Every scene boundary must be *authored*:

1. **Connective tissue is script.** Each scene's last line or next scene's first line carries the
   hand-off — an open question, a carried motif, or a motion that continues ("that lever? Now
   put a person on it"). The transformer emits `transition.in` + `motif` per scene; a boundary
   with neither a verbal nor visual hand-off is a defect.
2. **Continuous is the default.** Consecutive compatible scenes render as one unbroken sequence
   (`transition.in: continuous`); `hard_cut` is reserved for act boundaries and deliberate
   pattern interrupts, and the guard counts them (>1 hard cut per act = reject).
3. **Cast persistence.** Recurring characters keep identity across scenes (`cast:` ids in
   parameters) — the same uke walks between scenes; he does not teleport or respawn.
4. **Audio never cuts.** Music bed and room tone are continuous across the full video; only
   visuals change at boundaries.
5. **No dead first frames.** Every scene opens already in motion (entrance animation, camera
   drift, or a moving element) — the ThemedScene contract requires visible motion within the
   first 0.5s. Static openings read as stalls and lose the swipe decision on shorts.

## 4. Visual trigger syntax

Beat sheets use inline markers, compiled to `beats[]`:

```
Narration: "Kano's students threw armored samurai techniques out — and kept the leverage."
[VISUAL: stick figure samurai gets thrown by Jigoro Kano]  →  { "action": "pose:kano_throw" }
[VISUAL: lineage tree branches Brazil → Seattle]           →  { "action": "map:lineage_branch" }
```

Rules: every marker must resolve to a **named action or pose that exists** in the scene-class
registry / `assets/poses/` (guard-checked — a marker that resolves to nothing is a build error,
not a silent skip). `at_word` anchors are resolved after TTS from the word-timing arrays.

For grappling instruction, a pose marker alone is insufficient. Technique beats should resolve to
an anchored action marker with cast, state, and shot coverage, for example:

```json
{
  "at_word": 4,
  "action": "bjj_action:two_on_one_wrist_control",
  "cast": {"attacker": "white_gi_blue_belt", "defender": "black_gi_purple_belt"},
  "state_from": "closed_guard_posture_broken",
  "state_to": "wrist_control_hip_frame",
  "shot": "grip_closeup",
  "overlays": ["wrist_lock", "hip_frame_arrow"]
}
```

The transformer must prefer color-coded flat vector/chibi or technical infographic assets for
intertwined limbs. Generative image/video references may inform a shot recipe only when provenance
and permission are recorded; they do not replace the deterministic action/state contract.

## 5. Information gain (Golden Rule 2, made checkable)

Every long-form script must carry **≥3 only-here specifics** — facts a generic summary channel
cannot have: registry-derived counts, named lineages/academies with provenance, biomechanical
specifics (actual lever classes, actual joint structures), primary-source historical details.
Each is a `claims[]` entry. Gate A rubric scores this; scripts that are "Wikipedia with jokes"
get rejected regardless of polish. This is the moat restated editorially: **our fact layer is
the content advantage.**

## 6. Humor + persona (the accretive tier, not the slop tier)

- Recurring visual gags live in the pose library (`tap_frantic`, `gym_enforcer`, `bowler_hat_maeda`)
  so comedy compounds into brand. New gags = new poses = reviewed assets, not ad-hoc frames.
- Comedy attaches to *situations*, never to safety-critical or medical claims (a joint-injury
  scene may be vivid; it may not be a punchline).
- Write for the ear: short sentences, contractions, second person. Punctuation drives TTS
  pauses — em-dashes and full stops are pacing tools; walls of commas produce robot cadence.

## 7. Claims extraction (runs inside transformation)

The transformer must emit the `claims[]` ledger alongside the script: every number, superlative,
medical/financial/historical assertion → ledger entry with source from the fact layer, or the
sentence is cut/rewritten as instruction. Credential framing without a real named `expert` is
banned at the spec level (don't write it; the guard will reject it anyway). Unresolved claims
surface at Gate A as "needs source" — the operator sources or cuts.

## 8. Condensation heuristics (2,000 words → 750)

1. One spine idea per minute of runtime; everything else is cut or becomes a beat.
2. Lists collapse to their best exemplar ("fiber splicers, pipefitters, riggers…" → one splicer
   character, one number that survives the claims check).
3. Stats become visual comparisons (say the diagram, don't read the spreadsheet).
4. Anything the visual already says is deleted from narration — no narrating the obvious.
5. The essay's conclusion usually contains the video's hook.

## 9. Gate A rubric (human, ~5–10 min)

| Dimension | Question | Scored |
|---|---|---|
| Hook | Would *you* keep watching past 5s? Is the hook the strongest frame? | 1–5 |
| Angle originality | Is this a source-backed inversion with a human-owned thesis, rather than a copied outlier? Does any claimed skill stack feel earned? | 1–5 |
| Arc | Is there a real conflict/misconception, and does the comeback earn the payoff? | 1–5 |
| Information gain | ≥3 only-here specifics present and load-bearing? | 1–5 |
| Pacing | (machine-verified budgets) any dead stretches on read-through? | pass/fail |
| Flow | Does every scene hand off to the next (motif, question, or motion)? No orphan jumps? | 1–5 |
| Claim safety | (machine-verified ledger) anything that *feels* overclaimed? | pass/fail |
| CTA | Single, natural, earned? | 1–5 |

Publish threshold: no dimension below 3, machine checks green. The rubric result is stored in
`job.json` — over time it becomes training data for what the operator's bar actually is.
