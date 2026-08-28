# Audio Fix Runbook — `current-bubble-mechanism` mispronunciation

> **STATUS: DEPRECATED.** Kept for the reasoning trail; superseded by **37 §8**, Recording Standards v2 (master-take rule; splice-repair banned). Do not follow this document as current doctrine.

Status: ready to execute
Written: 2026-08-22
Scope: fix one mispronounced word without re-recording a 16-minute episode

## The defect, located exactly

Word **#811**, `"won"`, at **324.521–324.799s**, read as the past tense of *win*
rather than the Korean currency.

Its enclosing sentence:

> "The Korea Exchange recently showed roughly 5,370 trillion won of listed market
> capitalization."

| | |
| --- | --- |
| Span | **320.643s → 326.924s** (6.281s) |
| Size | **94 characters — 0.64% of the episode** |
| Seam gap before | 0.813s |
| Seam gap after | 0.511s |
| Median sentence gap (177 sentences) | 0.383s |
| Containing take | **scene_9002** (covers 266.0–515.3s) |

Both seams sit well above the median gap, so the sentence is a clean splice
candidate — *provided the source is a narration stem*. See the blocker below.

## Source artifacts

| Artifact | Path (relative to the pilot dir) |
| --- | --- |
| Word timings (authoritative, 2,445 words) | `audio/canonical/history_episode_1_master.words.json` |
| Canonical audio contract | `audio/canonical-audio.v1.json` |
| Narration master (`full_text`) | `audio/current-bubble-mechanism-narration-master.v1.json` |
| Per-take timings | `audio/canonical/takes/scene_900{1..4}.words.json` |

Pilot dir:
`C:/Users/Snipe/.codex/worktrees/p29-remotion-console/Outreach Program/content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism`

## Blocker: there is no narration audio on disk

Searched the whole pilot directory — **no `.mp3`, `.wav` or `.m4a` exists**. Only
word timings. The `audio_path` and per-block `audio_path` values in
`canonical-audio.v1.json` point at files that are not present, and there is no
`audio/canonical/blocks/` directory at all.

**And the final render's audio cannot substitute.** Measured on
`current-bubble-episode-one-full-p34.mp4` (one AAC stream, 981.013s):

| Segment | Mean | Max |
| --- | --- | --- |
| Gap before the target sentence | −28.5 dB | −8.9 dB |
| Speech | −23.2 dB | −6.9 dB |
| Gap after the target sentence | −22.9 dB | −6.0 dB |

The seams are ~5 dB below speech and the trailing gap is effectively at speech
level, so a music or ambience bed runs continuously underneath. Those are not
silences. Splicing narration into that track would cut the bed audibly.

**Get the stem.** In order of preference:

1. **ElevenLabs history** — `GET /v1/history/{history_item_id}/audio` returns the
   original narration, stem-clean. Free to pull.
2. **Re-synthesise take `scene_9002` only** (249.3s) — avoids splicing entirely.
3. Locate the stem wherever it actually lives; it is not in this worktree.

## Structural notes

- The 99 "blocks" in `canonical-audio.v1.json` are a **derived 10-second timing
  partition**, not separate recordings. The episode was recorded as **4 scene
  takes** (9001: 266.0s, 9002: 249.3s, 9003: 259.3s, 9004: 206.2s = 980.806s).
- Block `word_timings` **overlap** — 99 blocks sum to 4,889 entries against a
  2,445-word master. Always read the master `words_path`; never reassemble from
  blocks. `canonical_coverage_ingest.flatten_word_timings` already prefers the
  master when given `project_root`.
- `canonical-audio.v1.json` carries `storyboard_hash: ""`. The schema treats absent
  as valid but empty as invalid; the ingest service normalises this.

## The pronunciation rule

The obvious rule is **dead**. `preview` against the real 2,445-word script:

| Candidate rule | Matches |
| --- | --- |
| `"Korean won"` | **0** — the script never says this |
| `"won"` | 1 — safe here, but would fire on "he won the race" in a later episode |
| `"trillion won"` → `"trillion wahn"` | **1**, correctly scoped |

Use the scoped rule:

```json
{
  "string_to_replace": "trillion won",
  "type": "alias",
  "alias": "trillion wahn",
  "note": "ep1 read as past tense of 'win'; scoped to the currency context",
  "added_episode": "current-bubble-mechanism"
}
```

**Alias, not phoneme.** The episode was recorded on `eleven_multilingual_v2`,
which **silently ignores phoneme tags**. Phoneme rules only work on
`eleven_flash_v2` and `eleven_v3`. The operator is moving to v3, at which point
phoneme rules become available — but this alias works on every model, so use it
regardless.

## Procedure

1. **Obtain the stem** (see blocker above). Verify it before use:
   inter-word seams must sit at least 20 dB below the speech mean.
2. **Build the dictionary** and confirm the rule fires:
   ```bash
   python -m content.video_engine.cli preview-pronunciation --dictionary <dict.json> --script <script.txt>
   ```
   Expect `trillion won` → 1 match, no dead rules.
3. **Sync it** — `compile-pronunciation-sync` emits the request body; the operator
   or run agent performs the call, then `record_sync_result` persists the
   `dictionary_id` and `version_id`.
4. **Re-synthesise** either the 94-character sentence (splice) or all of
   `scene_9002` (no splice) with the dictionary attached.
5. **Patch and re-time.** T18 is specified but **not built** — see the plan. Until
   it exists, splicing and the downstream word-offset rebuild are manual.
6. **Re-time coverage automatically**:
   ```bash
   python -m content.video_engine.cli ingest-canonical-audio --coverage <estimated.json> --audio <canonical-audio.v1.json> --brief <brief.json> --output <job> --project-root <pilot dir>
   ```
   This re-derives every slot boundary from the patched word timings. **No plate,
   storyboard or render artifact is edited by hand.**
7. **Re-mix**, then re-render.

## What re-timing already guarantees

`ingest-canonical-audio` reconciles the read against the attested script before
accepting it, so a re-record that drifted from the script is rejected rather than
silently re-timed. A re-record with *identical* text reconciles cleanly — only the
timings change, and everything downstream follows automatically.

Proven on this episode: the estimate put it at 1047.794s across 223 slots; measured
came back at **980.806s** — 67s and 6.8% out. That gap is why render never runs off
the estimate.

## Related

- `.claude/PRPs/plans/P14-DIRECTOR-AND-SCENE-BOARD.plan.md` — T15 (built), T17
  (built), T18 (specified, not built)
- `content/video_engine/src/services/canonical_coverage_ingest.py`
- `content/video_engine/src/services/pronunciation_dictionary.py`
