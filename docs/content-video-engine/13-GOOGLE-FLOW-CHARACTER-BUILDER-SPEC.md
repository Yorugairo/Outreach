# Google Flow Character Builder — P13 V4.1

The History of BJJ lane now treats Google Flow's character builder as an
optional producer for recurring illustrated people. It solves a different
problem from plate animation: a character sheet establishes a repeatable
silhouette, costume, palette, and prop before a short video clip is attempted.

## Contract

`flow_character_pack.v1` is the durable input contract. The acceptance pilot's
packet is [`episode-1-flow-character-pack.json`](../../content/video_engine/projects/history-of-bjj/episode-1-flow-character-pack.json).
It binds four cast roles to the active art-bible hash:

- a fictional Registry learner;
- an illustrated reconstruction of Jigoro Kano;
- an illustrated reconstruction of Mitsuyo Maeda; and
- a named-person-free Brazilian composite.

The prompts specify views, palette roles, props, silhouette constraints, and
negative prompts. They intentionally ask for an illustrated reconstruction;
generated pixels are not archival evidence. Historical characters are not
required to reproduce a photograph and must be labeled as illustration or
reconstruction in editorial treatments.

## Browser workflow

1. Open Google Flow's character builder and select **Nano Banana Pro**.
2. Copy one character's `prompt` into the builder. Generate the character sheet
   before requesting motion. Do not paste research URLs, source frames, creator
   prompts, or citation text into the builder.
3. Review the front, three-quarter, profile, full-body, and expression/prop
   views. Reject face drift, costume drift, ambiguous hands, logos, lettering,
   and accidental historical claims.
4. Export the approved sheet to the job-local quarantine directory, record its
   SHA-256 and acquisition metadata, and leave `render_eligible: false` until
   the asset-manifest promotion review.
5. Use the approved sheet as a Flow ingredient for short, single-action clips.
   The clip prompt describes only the reviewed action and timing; Remotion
   adds narration, captions, citations, and credits.

The first test should be one learner sheet and one 8–10 second clip. Flow's
reference-to-video modes may expose a shorter duration than the editorial
10-second block; pad a shorter provider clip with a local held end frame rather
than asking the model to invent a second action.

## Style and editorial rules

The character pack is bound to `combat-history-longform-cutout-fork-v1` and its
internal atoms. The visual target is original woodblock-informed branded
literature: bold carved ink contours, warm paper, restrained indigo/rust/jade
accents, angular cutout anatomy, and prop-led acting. It is not a creator
imitation prompt and does not ingest the YouTube Reference Pack.

Use Flow characters for:

- map-to-character transitions;
- a learner reacting to a historical correction;
- a short illustrated reconstruction of a place, journey, or teaching moment;
- chapter cards and recurring margin gags.

Do not use them to teach a multi-step grappling technique, fabricate a quoted
document, draw a sourced map or lineage graph, or replace a rights-reviewed
archive. Manim/Remotion still own deterministic maps, relationship verbs,
citations, and typography.

## Promotion boundary

The pack, generated sheet, and provider clip are non-renderable until an
operator reviews them. Promotion requires:

- content hash and job-local containment;
- `source_kind: generated_original`;
- explicit fictional, historical-reconstruction, or composite likeness status;
- illustration/reconstruction label in the treatment;
- no logos or living-person likeness without separate approval; and
- a selected scene use that does not make the generated image evidence.

Once approved, copy the bytes into the job's generated-asset directory, keep
the original provider record in quarantine, add the promoted file to the
rights-reviewed `asset_manifest.v1`, bind the same SHA-256 to the character's
`reference_asset_ids`, and refresh the episode's manifest hash. The provider
record remains non-renderable; only the separately promoted manifest asset may
reach a renderer.

The producer plan adds `google_flow_character` and
`google_flow_ingredients_to_video` only when a validated `character_pack_id` is
configured for the series lane. Existing V1–V4 jobs remain unchanged.

## Local character-in-scene motion

The editor's `DocumentaryShot.character_layers` contract is the provider-neutral
motion fallback and the first production integration point. Each layer names an
approved asset ID, a bounded time range, a normalized position/size, and one
simple entrance (`enter_from_left`, `enter_from_right`, `rise`, `pop`, `settle`,
or `float`). The layer is resolved through the local asset map; URLs, Flow
prompts, and provider task IDs cannot reach Remotion. This keeps the historical
plate stable while the learner or reconstructed person enters, reacts, or
gestures over it.

The bounded proof is recorded in the P13 plan under `character-motion-sample/`.
It uses local crops derived from the approved learner and Kano sheets, has no
provider calls, and remains `awaiting_operator_sample_review` until the motion
is accepted for reuse.

## Credit accounting

Pricing is recorded as Flow credits rather than as a dollar estimate. In the
signed-in account observed on 2026-07-31, Google One showed 1,050 Flow credits
(1,000 plan credits plus 50 daily complimentary credits). The Flow generation
menu showed 15 credits for a 10-second Ingredients-to-Video Omni Flash x1 clip
and 20 credits for a Veo 3.1 Fast x1 clip. A bounded Omni Flash test debited
exactly 15 credits but failed at 11% without producing a downloadable output;
the evidence manifest is under the Episode 1 job's
`character-motion-production/google-flow-10s-test/` directory. The historical
Magnific/Kling `$14` value is an approval ceiling for that separate provider
path, not a per-block Google Flow cost.
