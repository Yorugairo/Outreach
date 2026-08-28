# Content video engine — document index

43 files live here. **Fewer than half are current doctrine.** This index
says which is which, because the numbering does not — numbers are creation
order and carry no meaning about status or priority.

Every document is one of three things:

| Status | Meaning |
|---|---|
| **DOCTRINE** | A live rule set. Maintained. Follow it. |
| **RECORD** | A point-in-time note, review or plan. Not maintained. Read it for *how* a decision was reached, never for what to do now. |
| **DEPRECATED** | Superseded. Kept only for the reasoning trail. |

RECORD and DEPRECATED files carry a status banner at the top. Nothing is
deleted — the archive is cheap to keep and expensive to reconstruct.

---

## Start here, not at doc 00

The working doctrine is **not** in this folder. It is three files in
[`docs/portable/`](../portable/), and they are the primary source:

| File | Size | What it carries |
|---|---|---|
| **`DOCTRINE-CORE.md`** | 9,999 chars | Channels, narrator, retention clock, six-phase architecture, sentence gates, packaging, production standards, never-list |
| **`OPERATOR-RULINGS.md`** | ~12k | Every standing correction, with the reason it was made |
| **`VOICE-PACK.md`** | ~10k | Voice by exemplar and contrast pair, plus the calibration protocol |

They are model-agnostic and sized to paste into a system-instruction box.
When a document in *this* folder disagrees with the portable tier, the
portable tier wins.

## The two layers (the organising principle)

Operator, 2026-08-28: *"everything we've been learning about how to build
the worlds + evidence layers is meant to be transferrable across all of
our channels and series."*

That splits every document here in two:

| Layer | Applies to | Docs |
|---|---|---|
| **Production — universal** | Every channel, every series, forever | **26** loop · **29** worlds, docks, motion · **37** recording · **39** evidence documents · **40** audit beat |
| **Scripting — lane-specific** | One lane's theme, audience, voice | **10** history/documentary · **31 · 35 · 36 · 38** finance formats and persona · **32 · 33** craft and voice |

A lane is never retired because its *production* pattern was replaced —
the production layer was never lane-specific in the first place. The
history lane is live; it is simply outside the finance set right now, and
it inherits **29** and **39** wholesale the day it ships again. The same
is true of Martial Matters and Building Money: they do not get their own
world or evidence standards, they get these.

## DOCTRINE — the live set

| Doc | Subject |
|---|---|
| **26** | Agent generation loop — claims, work orders, the review gate |
| **29** | Evidence & motion standards — the production bar for every channel. **Start at "Current state" at the top**; Part 9 below it is the amendment trail |
| **30** | Voice source material — the evidence the voice profile is derived from |
| **31** | Faceless channel doctrine (platform layer) |
| **32** | Writing for the ear (craft layer) |
| **33** | Voice profile |
| **35** | Answer-format doctrine — credit, steelman, relocate |
| **36** | Writer persona |
| **37** | TTS delivery standards — §8 is Recording Standards v2 |
| **38** | Script architecture — the six phases |
| **39** | Evidence chart system — palette, type scale, the three document species |
| **40** | Process as evidence — the audit beat |

Plus [`patterns/`](patterns/): the script pattern kit, phase guides P1–P6,
the sentence strength check, and the full video map.

## Supporting specs (live, narrower scope)

**03** system architecture · **08** tooling alternatives · **11** archival
asset & citation spec · **13** Google Flow character builder · **19**
hyperframes lane · **24** composition & scale · **27** durability & layout

## DEPRECATED

| Doc | Superseded by |
|---|---|
| **17** timestamped plate production | **29** Part 8–9 — held stills with hard cuts are a defect |
| **22** audio fix runbook | **37 §8** — master-take rule; splice-repair banned |

**Partially superseded:** **16** editorial motion system — its motion
pattern is now **29**, but its timing authority, plan contract, provider
boundary and QC sections still apply.

## RECORD — not maintained

**00** brainstorm · **01** PRD · **02** content strategy · **04**
storyboard contract · **05** competitive brief · **06** script
transformation spec · **07** pilot season · **09** YouTube reference-pack
learnings · **12** Higgsfield explainer learnings · **14** Higgsfield
audio-driven lane · **15** living-scene communication language · **18**
graphic-silhouette woodblock spec · **21** art-style reference review ·
**23** EP1 library intake review · **25** editor embedding spike · **28**
AOY MCP evaluation · **34** AOY script-writer study · **P13** gate A/B
armbar reviews

Twenty of these were written on 2026-08-02 and never revisited. That is
the correct lifecycle for a planning document — it is not a defect, but it
is why they must not be read as instructions.

---

## Rules for adding to this folder

1. **Amend before you number.** A new ruling on an existing subject
   belongs in that subject's doc plus `OPERATOR-RULINGS.md`. A new number
   is for a genuinely new subject only. (Docs 39 and 40 were both created
   in a single day; the second could arguably have been a section in 35.)
2. **A doc that stops being followed gets a STATUS banner** the day it
   stops, with a pointer to what replaced it.
3. **Numbering is append-only.** Never renumber — every path in this repo
   and in commit history points at these names. Number 20 is missing and
   stays missing.
4. **If a rule matters, it goes in the portable tier**, not only here.
   This folder is where reasoning lives; the portable tier is what gets
   loaded.
