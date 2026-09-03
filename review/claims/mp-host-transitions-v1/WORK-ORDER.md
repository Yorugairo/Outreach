# Work Order — claim `mp-host-transitions-v1`

Follow this document exactly. It is self-contained: generate, derive, self-judge,
deliver. Channel: **money-physics** (an identity wall — nothing here resolves into
another channel). Style family: `woodblock-vox-newsprint-v2`.

**What this claim makes.** The first entries of two reusable libraries, and the
first day's measurement of what a clip costs:

- **Transition clips** — the in-episode HOST (an approved flat graphic silhouette,
  five poses on disk) entering an approved world plate. Exits are derived locally
  by reversal, so one generation yields both. A transition ends or begins
  **pixel-exact on the approved plate**, which is what lets the live renderer take
  over with the chart docking through the template. That is the whole trick, and
  it is why this belongs to the world lane and not the evidence lane.
- **Hook clips** — three variants of the opening 0–8s for the Steel and Paper
  re-post, on the episode's title world, ending exactly on the plate so the first
  chart can land spotlit at E24's 8–20s window. Hooks are **line-agnostic**: no
  text, no mouth, no on-screen figure, so the hook sentence can be rewritten
  without regenerating the picture.

**The robo is not in this claim.** The robo is the thumbnail cover (packaging
playbook, mascot slot). The host lives in the episode. Keep them apart.

## Preconditions (check, do not assume)

1. The driver's **dedicated automation profile** is up: Chrome launched with
   `--user-data-dir=C:\Users\Snipe\.flow-chrome-profile --remote-debugging-port=9223`,
   signed in to Google Flow (9222 on the default profile is only the driver's
   fallback). Verify: `curl -s http://127.0.0.1:9223/json/version` returns JSON.
   If it does not, STOP — the operator launches the browser; you never enter
   credentials.
2. The `video-engine` MCP server answers `tools/list` and exposes
   `create_flow_batch`.
3. Every reference path in `batch.json` exists on disk under the MAIN checkout
   (`C:\Users\Snipe\Downloads\Outreach Program`). If any resolves into a worktree
   path, STOP and report — the plate library was rebuilt from main on 2026-09-03
   and every path should be home.
4. **Note the Flow account's credit balance before the run.** The daily allowance
   is 50. This run's purpose includes measuring cost per clip.

## Reference images (read-only inputs)

Never write into these directories.

- World plates (approved, `finance-episodes-plates-wave-1/objects/`):
  `world-signal-box-dusk-v1.png` (the railway yardstick's title world),
  `world-korea-port-v1.png` (the memory-export monitor's world),
  `world-memory-fab-floor-v1.png`, `world-seoul-fab-skyline-v1.png`.
- Host poses (approved cutouts, `assets/generated/cutouts/`, 1024×1536 RGBA):
  `actor-host-point-right-v1`, `actor-host-present-open-v1`,
  `actor-host-explain-both-hands-v1`, `actor-host-arms-crossed-v1`.

**A world that has no approved plate gets no transition.** A new world is a plate
claim first, then a transition. Do not generate a world inside this claim.

## Stage A — Generate (two days, priority order)

**What the first live run taught (2026-09-03).** The driver submitted to Nano Banana 2
in Image mode because it never selected a mode and matched controls on the bare word
"Video" — which also matches the left nav's "View videos". Seven motion prompts became
stills (cost: 0 credits). The driver now SETS mode / sub-mode / model / count, reads
back the composer pill and the "Generating will use N credits" line, and REFUSES to
submit on Image mode, a wrong model, or a scene over `maxCredits`. Flow quoted **24
credits at x2 / 8s / 720p on Omni 1.1 Flash**, so the library setting is **x1 / 6s**
and a day is roughly four clips, not seven. **Measured on the first verified submit: 10 credits per 6s clip at x1 / 720p** — fifty a day is five clips; day one's four cost forty.

- **Day 1 — `batch.json`:** the four host entrances, x1, 6s, 720p, Omni 1.1 Flash,
  `maxCredits: 16` each.
- **Day 2 — `batch-hooks.json`:** the three hook variants, 8s, `reverse: true`. Test
  ONE variant in `submode: "frames"` with the plate as the END frame first — if Flow's
  Frames mode takes an end frame, it guarantees the handoff pixel-exact and retires
  the reversal trick for hooks and exits.

Call `create_flow_batch` with the day's file verbatim. If a scene is REFUSED, the
error names exactly what the driver saw — deliver that, do not work around it.

Hard rules carried in every prompt, and to be checked on every output:

- **No text, lettering, numerals, charts, axes or screens anywhere in frame.** A
  chart in a generated frame is a fabricated figure (E22, E25, E28: charts are
  code). Any such artifact is an automatic reject.
- **The host renders EXACTLY as the referenced cutout: the full-colour cartoon —
  navy suit, orange tie, glasses, locs.** He is never a silhouette and never
  re-costumed. Day 1 (2026-09-03) produced four silhouettes because the agent's
  prompt *described* the reference from a doctrine phrase belonging to another
  channel (doc 18, the combat-woodblock silhouette lane, status RECORD) without
  ever opening the file. 40 credits, all identity-REJECT.
  **Rule: a prompt that describes a reference is written from the opened image,
  never from memory of what it should be.** Open every reference before Stage A.
- **Never call him a "cartoon".** The identity test (v2, 10 credits) said "full colour
  cartoon" and Omni treated it as a style order: enlarged head, flat fills, a sticker
  outline, and the locs simplified to a crop. He is a *detailed illustration in the
  world's own ink-and-newsprint register*. Describe him from the opened image - suit
  texture, tie pattern, glasses, goatee, tied locs, proportions - and say he is drawn
  in the scene's register, not pasted on. (Operator, 2026-09-03.)
- **The locked-identity route is the renderer, not the model.** The shipped template
  already animates our cutouts on a plate deterministically - `plate_life` species,
  `scene-evidence-player.template.html` line 1955: stepped time, throw-and-land with
  squash, two-frame boil. A host entrance built there is pixel-exact, zero credits,
  zero drift. Flow earns its credits on what has NO locked identity: worlds, hooks,
  ambient. Generated host motion is a Quality-tier / Flow-Character experiment, not
  the library's default.
- **Because the host has a face, face and proportion drift across the clip is the
  live risk** — the earlier "no face, so survivable" reasoning was built on the
  wrong host. Multi-reference the cutout every scene; keep clips at 6s; and test
  Flow's **Characters** feature — the project already holds character cards — as
  the identity lock. That question is now worth the test it was not before.
- **The background does not move** in transition clips. Only the host moves.
- **No costume the pose cutout does not wear.** Scene 1 (2026-09-03) came back with
  a peaked railwayman's cap the model added to suit the world; the silhouette IS the
  identity, so a hat is drift. Every host prompt now says "bare-headed, no hat, no
  props" unless the referenced cutout carries one. Judge it on the sheet either way.
- Duration 6s for transitions, 8s for hooks; 16:9 throughout.

## Stage B — Derive exits (free, local)

For each completed `host-enter-<world>.mp4`, derive the exit with FFmpeg:

    ffmpeg -i clips/host-enter-<world>.mp4 -vf reverse -af areverse clips/host-exit-<world>.mp4

The exit now **ends on the exact approved plate**, which is the handoff frame.
This is one generation for two assets, and it is where the day's credits go
furthest. The known cost: a reversed stride can read as walking backwards. The
prompts ask for a lateral, minimally-articulated step to keep the reversal
legible. If a reversed exit reads wrong on the sheet, day two generates true exits
for that world — do not fix it by hand.

## Stage C — Self-judge, then contact sheet

Extract first, middle and last frames of every clip (ffmpeg `select`), tile them
into `contact-sheet.png` — one row per clip, labelled by id, enters and derived
exits side by side. For every clip record PASS/REJECT against:

1. Silhouette holds: single tone, no face, proportions constant first→last.
2. Handoff frame matches the plate: for hooks and exits the LAST frame; for enters
   the FIRST frame. Judge by eye on the sheet; note any drift.
3. Zero text / lettering / numeral / chart artifacts, anywhere, any frame.
4. Background static in transitions; motion reads cleanly at the duration.
5. Register matches `woodblock-vox-newsprint-v2` — grain constant across the clip,
   not a photoreal drift halfway through.

A REJECT is recorded, not regenerated inside this claim. Regeneration is a
day-two decision made on the sheet.

## Stage D — Deliver

Under `review/claims/mp-host-transitions-v1/`:

- `clips/<id>.mp4` and `clips/host-exit-<world>.mp4` (gitignored by the binary
  policy; they live on disk only).
- `contact-sheet.png`.
- `mp-host-transitions-v1.manifest.json` — `schema_version: review_manifest.v1`,
  `status: review_only`, `render_eligible: false`, `channel: money-physics`, one
  asset per clip with `kind` (`transition_clip` | `hook_clip`), `semantic`
  (`host-enter:<world>`, `host-exit:<world>`, `hook:steel-and-paper:<variant>`),
  `duration_s`, `handoff_frame` (`first` | `last`), the plate and pose it was
  generated from, the sha256 of the mp4, and your PASS/REJECT with one line why.
- `approvals.json` — `judge`, `credits_before`, `credits_after`,
  `credits_per_clip` (the delta over completed generations), and
  **`approved: []` left EMPTY.** `approved` is set by the operator, never by
  product code. The claim stays in quarantine until the operator rules on the
  sheet.

## What the operator decides on the sheet

- Which clips are approved (they become the first indexed transitions).
- Whether reversed exits are acceptable, or day two generates true exits.
- Which hook variant, if any, carries the Steel and Paper re-post — and whether the
  hook should sit on the thumbnail's own world instead of the title world.
- The daily plan, now that a clip has a measured cost: how many library
  transitions versus per-episode hooks the 50 credits buy.

## Follow-ups this claim creates (not part of it)

- `build_plate_library.py` does not index `.mp4`. Approved clips need either an
  extension of it or a sibling clip index with the same channel wall and the same
  "status from the manifest, never the path" rule.
- `.gitignore:77` ignores `content/video_engine/**/review/` wholesale, so the
  approval manifests for 46 earlier plate waves are untracked. This claim sits
  under the repo-root `review/claims/`, which IS tracked, so its records are
  versioned. Whether to un-ignore `*.json` / `*.md` under the older path is an
  operator policy call.
