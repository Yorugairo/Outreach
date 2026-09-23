# Multi-Scale Strength Loop (L0–L6)

## 1. The 7 Scales of Script Review

- **L0 Line**: 10 Standing Sentence Gates (one idea, active concrete subject, no throat-clearing, numbers carry units, terminal stress on key noun/verb).
- **L1 Phrase**: Rhetorical cadence (attribution-first, anaphora arcs, tricolon completions, zero lazy filler).
- **L2 Beat**: Ira Glass anecdote/reflection alternation; every beat has a cause (`BUT` / `THEREFORE`, never `AND THEN`).
- **L3 Section**: Tension banking; evidence stacks toward the upcoming structural turn.
- **L4 Phase**: P1–P6 duty rosters verified against temporal windows.
- **L5 Video**: Chiastic balance (P2 mirrors P5 around the P4 pivot); Ring Echo transforms opening image; grand payoff at 60–70%.
- **L6 Catalogue**: Cross-episode distinctness; no repeated theses or colliding calls across channels.

---

## 2. Cross-Scale Checks (X1–X5)

- **X1 Pacing & Density**: WPM within channel bounds (~160–180 spoken WPM); mean shot duration ~10–12s (ceiling 20s).
- **X2 Pronoun Drift**: Every pronoun has an unambiguous antecedent in the preceding clause.
- **X3 Deictic Anchors**: Spoken references to visual evidence (*"this number"*, *"that spike"*) precisely match screen assets.
- **X4 Number Fatigue**: Never stack more than 2 raw numbers in a single sentence without a tangible comparison.
- **X5 The Tell**: The predictive call carries all 4 components: variable, numerical threshold, current position, and flip condition.

---

## 3. Screens Enumeration Mandate

Before Round 1 and after every edit round, emit the screens artifact:
```bash
python content/video_engine/scripts/enumerate_strength_screens.py <script_path>
```
The resulting `<script>-SCREENS.md` must be cited with exact counts in every convergence report.
