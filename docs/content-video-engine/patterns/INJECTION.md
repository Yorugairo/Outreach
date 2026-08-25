# INJECTION — the kit's parameter surface

The phase guides (P1–P6) are lane-agnostic generation contracts. Everything
channel-specific enters through this injection block, assembled ONCE per
script and passed to every phase. A guide may never assume a fact that is
not in this block or in the ledger chained from the previous phase.

## The block

```
INJECTION v1
============
RUNTIME_MIN:      <integer minutes> — drives every geometry table
TIER:             T1 8–10 | T2 12–18 | T3 20–30  (beyond 30: repeat P3 blocks
                  with mini-pivots; one true midpoint at global ~50%)
FORMAT:           standalone | serialized-segment | answer-to-a-channel
TOPIC:            one claim cluster + ONE dramatic question, stated as a
                  question the viewer needs closed
VOICE:            the voice-profile block — register, rhythm norms, humor
                  placement, the never-list (banned constructions)
PERSONA:          narrator block — biography usable as twist material,
                  standing theses, dissent etiquette, the lens (how this
                  narrator uniquely SEES the subject)
EVIDENCE:         verified figures, each with its source named — the only
                  claims the script may assert without a [verify] flag
ENTITY_SEED:      one adjacent authority/channel/name to invoke (passed
                  authority + topic-graph adjacency); ZERO or ONE, never more
TELL:             the falsifiable claim — variable + threshold + current
                  position + flip condition (consumed by P5)
RING_TOKEN:       optional — one concrete filmable object that opens the
                  video and closes it transformed; if absent, P1 chooses
                  and records it in the ledger
ANAPHORA_SEED:    optional — a candidate constant-opening phrase; if
                  absent, P1/P3 may coin one
NEXT:             serialized/bridge only — the next segment's promise
                  material (consumed by P6's Cliffhanger Bridge)
```

## Rules of the surface

1. **Nothing else enters.** If a phase needs a fact not present here or in
   the incoming ledger, the injection was incomplete — fix the block, do
   not let the writer improvise facts.
2. **EVIDENCE is the attribution-first gate's fuel.** A claim outside
   EVIDENCE carries `[verify]` and is banned from the microhook, the
   promise, the pivot's reversal, the payoff, and the tell.
3. **VOICE and PERSONA are prose lenses, not structure.** They may change
   how any line sounds; they may never add/remove structural duties.
4. **One block per script.** Phases share the same injection; only the
   ledger evolves between them.

## Worked example — finance lane (condensed)

```
RUNTIME_MIN: 8       TIER: T1        FORMAT: standalone
TOPIC: "Your index fund stopped being diversified." Question: if the S&P
  500 is 500 companies, why does one trade decide your retirement?
VOICE: spoken narration, faceless channel; direct, compressed, concrete;
  humor playful in setup, cutting on the landing; never: "let that sink
  in", fake curiosity hooks, greetings, "in this video".
PERSONA: ex-bank risk analyst who later ran a cash-heavy small business,
  now builds with AI; sees rooms and products as risk systems; dissents
  only when the market prices growth as weakness; acknowledges giants
  before departing from them.
EVIDENCE: top-10 weight ≈ 40% of index value (S&P Dow Jones Indices,
  2025) · >$500B retirement savings in one S&P 500 fund (Vanguard fund
  reports).
ENTITY_SEED: none
TELL: variable = top-10 index weight · threshold = 45% · position = ~40%
  and rising · flip = two consecutive quarters of breadth widening.
RING_TOKEN: (let P1 choose)
```

## Worked example — BJJ lane (condensed)

```
RUNTIME_MIN: 12      TIER: T2        FORMAT: standalone
TOPIC: "The white belt who trains three days a week beats the one who
  trains six." Question: why does the mat reward the one who shows up
  less?
VOICE: gym-floor register; technical terms pronounced, never dodged;
  humor self-deprecating in setup, precise on the landing; never:
  guru-speak, "mindset" abstractions, montage clichés.
PERSONA: hobbyist purple belt with a day job; sees training as load
  management, not heroics; lens = recovery economics — the body as a
  budget.
EVIDENCE: published overtraining/recovery findings with named journals ·
  gym-attrition figures with named source; anything anecdotal is framed
  as first-person experience, never as data.
ENTITY_SEED: one named competitor or coach whose published training
  split is citable.
TELL: variable = weekly training days · threshold = the point where
  session quality drops (measured by rounds completed) · position =
  narrator's current split · flip = a month of logs showing otherwise.
RING_TOKEN: the athletic tape roll on the gym bench (opens wrapped,
  closes half-used).
```

## Assembly order (who fills what)

1. Operator/produce: RUNTIME, TIER, FORMAT, TOPIC, EVIDENCE, TELL,
   ENTITY_SEED — the editorial decisions.
2. Standing blocks: VOICE, PERSONA — reused across scripts in a lane,
   versioned separately.
3. Writer-chosen (recorded back into the ledger): RING_TOKEN,
   ANAPHORA_SEED when absent.
