# 38 — Script Architecture: the deterministic prompt structure

Operator thesis (2026-08-24), and this document's organizing principle:

> "The secret sauce is that these tried methods from the research stand the
> test of time — what we learned from YouTube is how we fill in the space
> between."

The classical frameworks (doc 32: McKee, Truby, Snyder, Glass, rhetoric,
ring) supply the load-bearing structure. The platform doctrine (doc 31)
supplies the *timing capillaries inside each structural phase*. Neither
substitutes for the other: the research's "0:00–1:30 Hook & Setup" is
correct as architecture and useless as a build instruction until the
3-second microhook, the 8-second decision, the quick return, and the
positional rehooks are placed inside it. This doc fuses them.

---

## 1. Audit — how the script skills address this today

Honest state, per the operator's question:

| Layer | Where it lives | Enforcement today |
| --- | --- | --- |
| Acoustic sentence rules (active voice, one idea, terminal stress, 15–16 words) | doc 32 §1, doc 33 Rhythm | **Manual.** Applied by hand in the persona pass; nothing lints for them |
| Macro frameworks (gap, midpoint, anecdote↔reflection, ring) | doc 32 §4–5 | **Manual**, and the timeline generator has no macro-loop encoding yet (doc 28 follow-up, still open) |
| Platform timing (ladder, rehooks, One Minute Wall, CTA rules) | doc 31 | **Manual** at write time; only the TTS layer (doc 37) is enforced in code |
| Voice/persona | docs 33 + 36 | Manual persona pass; `brand-voice` skill points at the profiles but produces prose guidance, not structure |
| Delivery | doc 37 | **Enforced in code** — pause compiler, ration warning, dictionaries |

**Are the skills built to write prompts, or to write themselves?** They
write themselves. `article-writing`, `content-engine`, and `humanizer` are
instruction sets a model follows directly to produce prose; none of them
emit a reusable, parameterized generation artifact. The repo already has the
right pattern for determinism — the **work order** (the slide-registration
WORK-ORDER produced a validatable deliverable from a one-page contract) —
but scripts have never had one. That is the gap this doc closes: §3 defines
the SCRIPT WORK ORDER, and §2 is its first phase template.

The delivery layer proves the thesis: pause marks were doctrine for a day
and unenforced; the moment they got a compiler and a ration warning, they
became real. Script structure needs the same move — **template in, lintable
artifact out.**

## 2. Phase 1 — THE OPEN (0:00–1:30), fully fused

The research blueprint says: Truby's Weakness & Need · Glass's Anecdote ·
short punchy sentences · attribution-first · pre-opener pause · direct
address · irony counterpoint. The platform doctrine says the same 90 seconds
contains a 3s microhook, an 8s decision, a 15s delay tolerance, a 30s
mini-payoff, and the One Minute Wall. Fused, beat by beat:

### Beat 1 — MICROHOOK (0:00–0:03)

- **The first sentence is the grab.** Present tense, viewer-facing, concrete,
  terminal stress on the surprising word. One cut. *"She earns half of what
  he does."*
- **Visual stun is simultaneous** (Dopamine L1, 0–2s): the plate is already
  moving. Never black, never a logo. The classical "pre-opener pause" is
  **bent into a visual-only breath** — the plate breathes ~0.5–0.8s before
  the first word; no cold silence (doc 32 §7).
- **Counterpoint from frame one**: the image does NOT illustrate the line —
  it tensions it (calm premise narrated over an anomalous image, or the
  inverse).
- Craft: McKee's gap opens HERE — the line must state something whose
  expected consequence the next line will violate.

### Beat 2 — QUICK RETURN (0:03–0:08)

- **Pay the microhook immediately, and pay it wrong.** The second line
  answers the first's implicit question with a violation of expectation:
  *"She retires first."* `[post-key]` — the settle pause is scripted, and
  it lands ON the 8-second decision boundary, so the viewer decides during
  the breath after the paradox, not during throat-clearing.
- By the end of this beat the viewer knows *what the video is about*
  (8s establish, doc 31 §1) — established by paradox, not by announcement.
- Ban list active: no greeting, no "in this video," no atmosphere
  (Delay Disease dies at 15s; we never get near it).

### Beat 3 — THE WORLD OPENS (0:08–0:30)

- **The anecdote engine starts** (Glass): chronological, concrete, sequential
  bait. Characters enter as archetypes-in-specific-settings — the banker,
  the budtender — never demographics. This is Truby's **Weakness & Need**
  planted as *people*: the instability the whole video will resolve.
- **Direct address enters**: "you" appears for the first time, converting
  spectator to participant.
- **Attribution-first** on any factual claim; specific numbers over vague
  amounts (a concrete number sparks the question).
- **Stakes named** by ~0:25 (hook anatomy: Target + Transformation + Stakes).
  Identity videos deploy **biography as the twist** here — after the
  paradox, never before it.
- Sentence mechanics fully active: one idea each, active voice, 15–16 word
  average in a wave.
- Curiosity gap must be **open and demanding** by 0:30 — the cliff
  diagnostic reads retention at this timestamp; 70%+ means these three
  beats worked.

### Beat 4 — MINI-PAYOFF + THE DATED PROMISE (0:30–0:60)

- **Deliver real value first** (One Minute Wall: 30–60 = mini-payoff AND
  bigger loop). The viewer gets a genuine partial answer — proof the video
  pays — before being asked to stay.
- Then `[pre-key]` and **the promise with a date**: "…it fits on a single
  receipt, and by the end of this video you'll calculate yours." This is
  the retention clock's 30s promise, the macro loop's Setup, and rehook
  slot #1 (positional doctrine: 30s) — one line doing three jobs.
- **The tricolon is licensed here** for the thesis line (rule of three,
  doc 32 §3) — this is the sentence the viewer should be able to repeat.
- The promise must be **calculable/checkable** — the falsifiable-tell
  discipline (doc 35) applied to the viewer's own life.

### Beat 5 — THE MAP, NOT THE TERRITORY (0:60–0:90)

- **Signposting without spoiling**: where this is going, framed as journey
  ("three rules… the first is hiding on every receipt you've thrown away"),
  never as table of contents. Tease the what, hold the how.
- **Truby's Desire and Opponent are named**: the goal the video pursues, and
  the antagonist — which in our lane is always a **mechanism** (an
  incentive structure, a compounding cost), never a villain (Principle of
  Antagonism, doc 32 §4).
- **Rehook slot #2** lands at ~1:00 (positional: 1min) — the "But here's
  where it gets weird…" family, re-justifying the next 60 seconds.
- **Context-dump ban enforced** (Deadly Mistake #2): any principle stated
  here must already be cashed into an object or a number; history and
  theory wait until something is working on screen.
- Phase exits with macro loop #1's Tension fully wound: a partial answer
  delivered, a bigger question open, and the first act's engine
  (Snyder's Catalyst) queued.

**Phase QC line** (goes into the work order as checks): first sentence ≤ 3s
and concrete · paradox lands by 0:08 · "you" appears by 0:30 · real value
delivered before 0:60 · promise carries a date/number · rehooks at ~0:30
and ~1:00 · zero greeting/announcement constructions · every abstract noun
cashed out within one sentence · pause marks placed (`[post-key]` after the
paradox, `[pre-key]` before the promise).

## 3. The full skeleton (phases 2–6, same fusion — to be expanded per use)

| Phase | Classical spine (doc 32) | Platform fill (doc 31) |
| --- | --- | --- |
| 2. ENGINE (1:30–~5:00) | Snyder Catalyst + Debate; McKee inciting incident; anecdote↔reflection alternation begins | New info every 15–30s; STR micro loops 30–60s; rehook slot #3 at 3:00; BUT/THEREFORE connectors |
| 3. THE GAP (Act II) | McKee expectation-reality gaps; Truby Opponent & Plan; anaphora across progressive points | Point ordering (best evidence mid-video); breathing-room dips; macro loops 4–6/15min |
| 4. MIDPOINT PIVOT (~50%) | Snyder false peak / false collapse; Truby Battle; dramatic sentence-length contraction | Mid-video rehook slot; visual register shift; the mid-video-cliff cure applied structurally |
| 5. REFLECTION (post-pivot) | Glass Reflection dominant; chiastic center — the transformative thesis | Savor beats carry `[post-key]` silence; foreshadowed payoff (hook → ~min 3 → ~min 8) culminates |
| 6. CLOSE (final ~90s) | Ring: echo the opening image transformed; Truby Self-Revelation & New Equilibrium; final anaphoric triad | Peak-End; Action Window (CTA 15–30s AFTER the payoff); ONE CTA; Story Close or Cliffhanger Bridge template; no padding |

## 4. The SCRIPT WORK ORDER (deterministic prompt structure)

The generation contract. A script is never "written" ad hoc; it is produced
from a filled work order, by whichever writer (this session, a fresh
session, `write_script_v2` + persona pass, or a future fine-tuned lane):

```
SCRIPT WORK ORDER v1
====================
inputs:
  topic / claim_cluster:   <claim ids from the registered vocabulary>
  format:                  explainer | answer (doc 35) | book | chart-story
  runtime_tier:            T1 8-10 / T2 12-18 / T3 20+   (doc 31)
  persona:                 docs/content-video-engine/36-WRITER-PERSONA.md
  voice:                   docs/content-video-engine/33-VOICE-PROFILE.md
  evidence:                registration pack refs; [verify] queue for new claims
  entity_seed:             one adjacent authority (or channel, for answer format)
  falsifiable_tell:        variable + threshold + current position + flip condition

phases:                    §2 template for phase 1; §3 skeleton rows expanded
per-phase checks:          the QC lines (phase 1's is written; others follow)

output contract:
  - narration with [pre-key]/[post-key] marks (compiled by doc 37 machinery)
  - beat sheet with per-beat timing + rehook slots marked
  - figures written out as speech; verbatim strings live on badges only
  - sources block for every figure (the write_script_v2 standard, adopted)

QC gates (run before production):
  structural: rehooks positional · one CTA · ring close present · macro
    loops counted · payoff foreshadowed 3x
  acoustic:   sentence-length average · passive-voice scan · terminal-stress
    check on beat-final lines · tautology scan (line captions its visual)
  slop:       doc 31 §4 audit + doc 33 never-list
  persona:    doc 36 §5 pass confirmed (thesis lens, de-tribalized,
    empowerment close)
```

Near-term implementation: the QC gates that are mechanically checkable
(sentence stats, passive scan, CTA count, mark placement) belong in a lint
script beside the pause compiler — same pattern, same reason: doctrine
becomes real when it has an enforcer.

## 5. Worked instance

The v5 hook + Alicia v2 persona pass
([briefs/ALICIA-SCRIPT-PERSONA-PASS.md](briefs/ALICIA-SCRIPT-PERSONA-PASS.md))
is Phase 1 of this architecture executed at 3:00 scale: microhook (0:03),
paradox on the decision boundary, world-open with archetypes, dated promise
on the receipt, map-not-territory into rule one. It was built by hand; the
work order exists so the next one is built by contract.
