# SENTENCE STRENGTH CHECK — the line-by-line gate

A per-sentence pass run AFTER a script conforms structurally and BEFORE it
goes to audio. The phase guides govern what each line must DO; this gate
governs whether each line is STRONG — every sentence is checked against
all ten gates below, and any sentence that fails any gate is rewritten
until it passes. No sentence ships on "good enough in context."

## Procedure

1. Extract narration only (no stage directions, no annotations).
2. Walk it sentence by sentence, in order. For each sentence, mark every
   gate it fails.
3. Rewrite the sentence. Re-check the rewrite against ALL ten gates (a
   fix for one gate often breaks another). Repeat until clean.
4. Log every rewrite: original → gates failed → final. The log is part of
   the deliverable — it is how the pass is audited and how the gate
   improves.
5. Re-run the mechanical lint on the finished script (rewrites can
   introduce fragment stacks or break the ring).

## The ten gates

| # | Gate | Fails when |
| --- | --- | --- |
| S1 | **One idea** | the sentence asserts two things a listener must hold separately — split it |
| S2 | **Active, concrete subject** | the grammatical subject is not the actor, or the verb is passive ("was aimed", "is expected") — name who does what |
| S3 | **Terminal stress** | the sentence ends on scenery, a qualifier, a date, or a trailing adverb instead of its most surprising or heaviest word — reorder so the punch lands last |
| S4 | **Cashed concreteness** | an abstraction stands uncashed — no object, number, name, or action in the sentence makes it touchable |
| S5 | **Earned length** | over ~22 words, or under 5 words outside a licensed contraction run — long sentences must be one cadenced breath, fragments must be deliberate |
| S6 | **The ear test** | read aloud it stumbles: homophone ambiguity, hissing clusters, a page-ism the mouth resists ("sources below", "see above", "the former") |
| S7 | **Attribution-first** | a factual claim leads with the assertion instead of its source |
| S8 | **The delete test** | deleting the sentence loses nothing a neighbor doesn't already carry — filler, throat-clearing, restated setup. Delete it |
| S9 | **Verb strength** | the verb is "is/are/has" plus an abstraction where an action verb exists ("is in decline" → "declines") — thesis-grade definitions are the one exemption |
| S10 | **The never-list** | any banned construction of the injected voice profile: bait questions, fake curiosity, stock commentary lines, greeting/meta constructions |

## The named-subject rule (operator, 2026-08-30)

**Specify the instrument, person, place, or thing.** Where a sentence
passes authority (an attribution), renders a judgment, or draws a
comparison, its subject must be NAMED — never a pronoun, never a bare
deictic. "Their second line" hands the chip industry to whoever the last
sentence mentioned; "the chart's second line" hands it to the chart.
"That's a new instrument" points at the nearest noun; "the yardstick is a
new instrument" points at the yardstick. Naming prevents ambiguity AND is
what lets authority transfer and comparisons land cleanly — a judgment on
a pronoun is a judgment on a guess. This is the WRITE-side rule behind
S2/S4 and the X1 screen: X1 catches the orphans; writing named subjects
prevents them. Pronouns remain fine for continuation within a beat — the
rule binds at authority, judgment, and comparison points.

## Licensed exceptions (must be claimed in the log, never assumed)

- **Contraction runs** (the pivot, the final triad): fragments and
  repeated structures are the figure — S5 relaxes, S3 does not.
- **Deliberate get/is-parallelism** inside a declared anaphora or triad
  ("gets used / gets believed / gets discovered"): S9 relaxes for the
  figure's spine only.
- **Enumerations that mirror a declared structure** (the answers to three
  numbered questions) are not rhetorical triads — but they still take
  terminal stress on the final item.
- **Chart-read fragments** ("Historically, two to four.") while the
  evidence is on screen: S5 relaxes, everything else holds.
- **Agent-hiding passive is never licensed** — when the point is that a
  system acted on the viewer, name the system ("they sold you the
  index"), which is stronger than the passive anyway.

## What this gate is NOT

It does not judge structure (duties, loops, ratios — the phase guides own
that), and it does not smooth voice into blandness — a sentence that
passes all ten gates in the injected voice is the goal, not a neutral
sentence. When a gate and the voice profile genuinely collide, the voice
profile wins and the exception is logged.
