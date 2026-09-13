---
name: flow-stills-first-image-to-video
description: "E40 (2026-09-05): image generation is the strong tool, video only by FRAMES (start + end still + chip), never ingredients; Flow character clips (2026-09-04): text-to-video with the chip alone has little consistency - roll stills x4 (free) first, operator approves a contact sheet, then generate each video FROM its still + chip; never write '@Name' in prompt text (the driver refuses it); the driver dedupes downloaded videos across scenes; the template has a clip world"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-05T06:30:10.295Z
---

Operator, 2026-09-04, on the Tokyo StickMike clips: *"there's actually little consistency in
generation. I think that's why most of the prompt packs we came across used image-to-image
generation for the video"* and *"you should be bulk generating the stills if you're not going
to use them to generate sequential scenes."*

**What happened:** six Omni 1.1 Flash clips with `references: ["StickMike"]` - one bound the
character, five drew a stranger (a purple-tee cartoon, a generic suit) and one printed the
literal "@StickMike" on the page. Cause: the prompt TEXT carried "@StickMike"; the driver had
already attached the chip, and typing the '@' re-opened the picker. Then the driver saved scene
1's video for scene 2 (the page lists the previous output after the baseline is taken).

**How to apply:**
- Prompt text never contains '@'. The character enters as the chip (`references`); the text
  says "the character" / "he". `cdp-driver.setPrompt` now refuses an '@' and verifies the chip
  BY NAME (a bare chip count passed a stale chip).
- Stills first, in bulk: `mode: image`, Nano Banana Pro, `count: 4`, 9:16, free (E36). Contact
  sheet via `content/video_engine/scripts/contact_sheet.py`; the operator approves; each video
  is generated from its approved still + the chip (ingredients). Sequential scenes may instead
  chain from the previous end frame (`chain_from_previous`).
- `waitForGenerationAndDownload` keeps `seenVideoIds` (media id before '?') so a downloaded
  video is never "new" again in the session.
- The player template has a CLIP world (`world.kind == "clip"`, a silent mp4 seeked to the
  scene clock; `window.__clipsSeeked` awaited by `render_baseline.frame_png`); the compiler
  takes `clip:<mp4>` plate ids and per-episode overrides (EP / BUILD / SHOT_TABLE_FILE / TITLE
  / ASPECT); `render_episode.py` takes RENDER_BUILD / RENDER_URL / RENDER_ASPECT / RENDER_NAME.
  Tokyo's build is `tokyo-tea-break/build_short.py` (rows anchored on phrases, cut at 0.8 of
  the gap, 0.25 s edit pauses where the take's gap is under 0.30 s).
Three more driver facts from the same night: the redesigned drawer has NO Image/Video toggle (the
model family dropdown sets the mode - Nano Banana Pro = image; a count regex built from a template
literal had a backspace in it); Flow's `/asb/` image URLs are 286x512 preview thumbnails, the render
is the `flow-content.google/image` URL; and scenes after the first in a batch drew the EARLIER scene
until `setPrompt` read the composer back (E29: verify what landed). Image-to-video from an approved
still holds the character (shot A, `clip-a-counter-tab-v2`).
See [flow-driving-consent](flow-driving-consent.md), [mp-host-identity](mp-host-identity.md), [gate-fit-mangles-prose](gate-fit-mangles-prose.md).

**Operator verdict, 2026-09-05 after the six clips landed:** *"all this flow process is proving is
that it's not the right path. we just burnt all day on it."* One day and ~12 driver fixes (drawer,
picker, chips, positional claims, seen ids) for six 10 s clips. **Do not drive Flow for per-shot
clips again without the operator asking.** The short's motion is E32's list: page flip, stage
captions, a push on an approved still - all deterministic and free. Stills (image mode, free,
verified by contact sheet) remain useful; video generation is the part that cost the day.

**Ruling E40 (2026-09-05, after the first full pass):** *"the image generation is very powerful,
the video generation is less so, and if it is going to be used, it has to be by frames, not
ingredients. Frames give us two points and a character to control the scene with."* And: *"I don't
know how much value these omni videos are actually adding - some of them we could do with our own
setup."* So: stills + our own motion is the default world; a clip is the exception and is driven by
a START and END frame (approved stills) plus the chip; ingredients mode is out for shots; before
generating any clip, check whether doc 29 / doc 47 / the ledger page already does the motion.

