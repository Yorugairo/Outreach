# 28 — Art of YouTube MCP: Trial Evaluation

**Decision at stake:** $3,800/month membership. Trial window: 2 weeks from
2026-08-24. Their pitch: cheaper hiring + the AOY toolset. Working
hypothesis (operator's): the tools are vibe-coded wrappers around Claude/GPT
calls — good frameworks, shallow execution — and the frameworks are
extractable during the trial.

**Evaluation frame:** moat vs. replicable. A tool only justifies recurring
spend if it holds data or infrastructure we cannot reproduce. A rubric in a
prompt is not a moat; a curated database might be.

## Scorecard (updated as tested)

| Tool | Tested | Verdict | Moat? |
| --- | --- | --- | --- |
| `review_script` | ✅ | Useful 8-axis rubric, weak AI-slop suggestions. The rubric is fully visible in output. | No — rubric extracted; our humanizer + judgment beat its rewrites |
| `review_title` | ✅ | Same shape: 7 criteria incl. <8-words rule. Suggested titles altered our factual claim. | No — criteria extracted |
| `Titles_Format_Library` | ✅ | Template fill-in, mediocre adaptations. All 150 patterns are on a **public static page** they link in every response. | No — public asset |
| `search_library` | ✅ | **Paywalled in trial.** The knowledge base — the one plausible moat — cannot be evaluated before paying. | Unknown, untestable |
| `ask_tim` | ✅ | Not coaching — it ignored the actual question and returned 9 raw doctrine chunks. As **extraction**, excellent: course content verbatim per question. | Content is real; delivery is RAG dump |
| `write_script_v2` | 🔄 running | Flagship. 30-45 min async, 3/day quota. Three-way comparison pending (see below). | TBD |
| `deep_channel_analysis` | ✅ | Fetches top-5-by-views transcripts + metadata; **the analysis itself runs on the caller's model and tokens**. Our `/watch` does transcripts *plus frames*. | No — convenience wrapper |
| `Niche_Hunter` / `full_picture` | ⬜ | Curated "proven channels" DB + live scan. The DB is the strongest moat candidate that's actually testable. | TBD |
| `clone_thumbnail` / `ab_thumbnail` | ⬜ | Gemini image gen behind daily quota — we already run a stronger generation loop (P17). | Almost certainly no |
| `voiceover` | ⬜ | Requires **our own** ElevenLabs key — they bill nothing, wrap the UI. | No |
| `hiring_funnel` | ⬜ | Their headline pitch. Generates job posts/scripts/benchmarks from Tim's docs. | Content real; one-time value, not recurring |
| Profile/course plumbing | ✅ | NEW_USER, empty; Copilot board unpersonalized in trial. | n/a |

## Infrastructure observations

- **Rate limit: 5 calls per 3 minutes across all tools.** At $3.8k/mo.
- Script quota 3/day; image quota daily.
- Responses embed instructions to the calling model (skill-file install nags,
  "share this link exactly as written"). Treated as data, never executed —
  standing MCP hygiene.
- The `aoy-coach.md` skill auto-install mechanism is declined by default: we
  do not install skill files pushed by an external server.

## The decisive test: three-way script comparison

Same title, same references, same 3-minute target:

1. **Ours** — the recreation brief script (humanizer + retention curve +
   operator's two-altitude voice), reviewed at 7/10 by their own reviewer.
2. **Theirs** — `write_script_v2` output:
   https://ai.theartofyt.com/reports/ee363e00d37f459f.html
3. **Ground truth** — Alicia's actual 0:00–3:00 (transcript on file).

Judged on: hook mechanics, retention architecture, voice specificity,
factual grounding, and how much post-editing each needs to be shootable in
our pipeline. If theirs does not clearly beat ours, the flagship is not worth
recurring spend — we already own generation, scan, render, and gates.

## Extraction plan for the trial window

What to harvest legitimately while access lasts (their tools emit this
content to us as a customer; we take notes like any student):

1. **Doctrine via `ask_tim`** — batched questions within the rate limit; each
   returns verbatim framework chunks. Already captured: Alicia signature patterns across her top 5 (vignette cold-open, 'I want you to picture' tic, data injection, numbered rules, compound-math beats, binary framing); 4-stage growth model,
   impressions-vs-views diagnostic, 5-stage format lifecycle, earn-your-right
   -to-experiment, lucky-shot vs untapped-niche test, past-self method,
   faceless-personality mechanisms, ceiling-pattern rule, metric hierarchy.
2. **The 150 title patterns** — public URL; mirror into our own title tooling.
3. **Review rubrics** — both already fully visible; fold into our script/title
   review skill.
4. **Channel SOPs via `deep_channel_analysis`** — run on our actual target
   and competitor channels; each run hands us a Channel_Reference.md we keep.
5. **Niche DB sampling via `Niche_Hunter`** — a handful of scans on niches we
   care about; the reports persist.

## Long-form script structure — what `ask_tim` returns (2026-08-24)

Probe: *"On a 16-minute finance explainer, where does the writing effort go —
hook and CTA, or the 13 minutes in between? How many retention devices between
minute 2 and 14, and what are they called?"*

Operator hypothesis going in: their prompting is really only about the opening,
the close, hooks and CTAs. **Half confirmed.**

### Confirmed: the templates stop before our runtime

Both named long-form structures are timestamped only to roughly the 12-13
minute mark before handing off to a CTA — one framed as a video essay
(10-15 min), one as a framework reveal (12-15 min). **A 16-minute script is
off the end of their map.** For our 16:21 cut their system prescribes nothing
for the final three-plus minutes. The likely Tim answer to "rewrite our 16
minutes" is *compress it to fit a template* — a formatting answer, not a
structural one.

### Not confirmed: the middle is managed, by cadence rather than content

Real constraints do exist for the middle. They are density rules, not content
architecture — the writer still decides what goes in:

- **STR loops** (setup → tension → resolution) nested at two scales: micro
  loops closing every 30-60s, and **4-6 macro loops per 15 minutes**, each
  closing on a partial answer that opens a larger question.
- **Rehooks every 60-90s**, BUT/THEREFORE transitions, varied sentence rhythm.
- **Point ordering:** open with a strong example but *not* the best, put the
  best in the middle where retention peaks, close with the third-best. Leading
  with the best leaves nowhere to go.
- **Retention-graph diagnostics:** five named failure shapes (cliff, slow
  bleed, mid-video cliff, re-engagement spike, plateau), each with a fix.
  Genuinely useful, and not hook-craft.

### Where this lands on the moat question

The point-ordering rule and the loop-density numbers are the most transferable
things extracted from `ask_tim` so far — real editorial constraints rather than
rubric text. They are also, once written down, ours. Consistent with the
running verdict: **content real, delivery a RAG dump, no recurring moat.**

The template ceiling is itself a finding. Their system is built for 10-15
minute videos; we are producing longer, so beyond that runtime we are on our
own regardless of membership.

### What our pipeline does not yet encode

Measured against the 16:21 p34 cut: one visual event every 9.2s (60 evidence
beats, 47 world beats over 981s). Denser than their 30-60s loop cadence — but
visual events are not narrative loops, and we currently have **no named macro
loops at all**. Structure is scene-and-evidence driven, so nothing holds an
open question across the middle.

Evidence distribution by third was 33 / 12 / 15 — front-loaded into exactly
the region the point-ordering rule warns about. **This is an artefact of asset
availability, not an editorial decision:** evidence clustered where usable
assets existed. Re-plan distribution once the slide-registration pack lands and
the full 86-slide catalogue is selectable. Do not read the current shape as a
choice.

Open follow-up: encode loop structure in `scene_evidence_timeline.v1` — a
macro-loop id per scene with its open/close beats — so the generator can report
loop count and spacing the way it now reports bare-plate gaps.

## Verdict (running)

Pending the script comparison and Niche_Hunter test. Early lean: the
**content** (Tim's frameworks) is real and largely extractable through normal
trial use; the **software** is thin wrappers with hobbyist limits; the
**price** buys a membership community and hiring templates, not
infrastructure. Our own stack already exceeds the generation half.
