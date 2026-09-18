# The 16:9 outro card — render notes

R26-210 (audit G-06, `docs/research/LONG-FORM-CAPABILITY-AUDIT-2026-09-18.md` §(c) item 4):
there was no landscape outro on disk. All four Tokyo movs
(`projects/systems-and-blowups/tokyo-tea-break/outro/{outro,outro-v2,outro-brand,outro-yt}.mov`)
are the same 1080x1920 portrait render. These two are the 1920x1080 siblings.

Rendered 2026-09-18 from `content/video_engine/remotion-kit/` (Remotion 4.0.502, the version
the editor pins). **The `.mov` files are gitignored** (`.gitignore` `*.mov`, anywhere in the
tree); this file and `outro-yt.props.json` are the record. Re-render with the commands below.

## What is here

| file | composition | geometry |
|---|---|---|
| `outro-yt-1920x1080.mov` | `OutroLandscape` | 1920x1080, 30 fps, 186 frames, 6.200 s |
| `outro-yt-1920x1080-24fps.mov` | `OutroLandscape24` | 1920x1080, 24 fps, 149 frames, 6.208 s |
| `outro-yt.props.json` | — | the props both were rendered with |

**Which one the build should use: `outro-yt-1920x1080-24fps.mov`** for the long-form cut,
because the long-form render is 24 fps (E99 s36) and this avoids a resample of the card.
Take the 30 fps file for any 30 fps timeline (it is the exact frame count of the shipped
portrait card). See "The 24 fps variant" below for the one behavioural difference.

## The command

From `content/video_engine/remotion-kit/` (the entry is `src/index.tsx`, which registers
`src/Root.tsx`):

```bash
# Dependencies are not declared in the kit's package.json (it is the bare scratchpad one),
# so install them without touching it or writing a lockfile. Install EVERYTHING in ONE
# command: a second --no-save install prunes the first one's packages as extraneous,
# because package.json declares no dependencies to hold them in the tree.
npm install --no-save --no-package-lock   remotion@4.0.502 @remotion/cli@4.0.502 react@18.3.1 react-dom@18.3.1   typescript@5.7.3 @types/react@18.3.18 @types/react-dom@18.3.5 @types/node@22.13.4

npx tsc --noEmit -p tsconfig.json   # exit 0 across all nine kit sources

# 30 fps
npx remotion render src/index.tsx OutroLandscape \
  ../channel-assets/money-physics/outro/landscape/outro-yt-1920x1080.mov \
  --codec=prores --prores-profile=4444 \
  --props=../channel-assets/money-physics/outro/landscape/outro-yt.props.json

# 24 fps
npx remotion render src/index.tsx OutroLandscape24 \
  ../channel-assets/money-physics/outro/landscape/outro-yt-1920x1080-24fps.mov \
  --codec=prores --prores-profile=4444 \
  --props=../channel-assets/money-physics/outro/landscape/outro-yt.props.json
```

`--codec=prores --prores-profile=4444` mirrors the portrait render exactly — `ffprobe` on
`outro-yt.mov` reports `prores / profile 4444 / yuv422p12le` plus a silent
`pcm_s16le 48000 Hz stereo` track, and both landscape files report the same.

## The props

`outro-yt.props.json` — the **`outro-yt` ("subscribe") variant**, i.e. the one the YouTube
re-upload uses:

```json
{
  "headline": "It's not magic.\nIt's mechanics.",
  "tagline": "Thanks for watching — subscribe for the next teardown.",
  "showHandle": true,
  "handle": "@MoneyPhysicsHQ",
  "nodeColor": "#a78bfa",
  "textColor": "#f5f5f5",
  "backgroundColor": "#030014"
}
```

**Where these came from.** No file in the repo records `outro-yt`'s props — `README.md` and
`CAPABILITIES.md:63` only say it "says subscribe". So they were **read off the shipped render
itself**: a frame pulled at t=4.0 s from `tokyo-tea-break/outro/outro-yt.mov` and compared
against the same frame of `outro-v2.mov`. The two differ in **one word** — `follow` becomes
`subscribe` — and match the `Outro` composition's `defaultProps` in every other respect
(headline, handle, `#a78bfa` nodes, `#f5f5f5` text, `#030014` ground). Hence: defaults plus
the one tagline override, passed at render time. The compositions' `defaultProps` are
unchanged, so `outro-brand`'s cream re-skin stays a `--props` override too.

## ffprobe

`ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,duration -of csv=p=0 <file>`

```
outro-yt-1920x1080.mov        1920,1080,30/1,6.200000
outro-yt-1920x1080-24fps.mov  1920,1080,24/1,6.208333
```

For comparison, the four portrait movs, same command:

```
outro.mov        1080,1920,30/1,6.200000
outro-v2.mov     1080,1920,30/1,6.200000
outro-brand.mov  1080,1920,30/1,6.200000
outro-yt.mov     1080,1920,30/1,6.200000
```

## The portrait parity check

`src/Root.tsx` gained two compositions; the `Outro` composition and
`src/NetworkNodesOutro.tsx` were **not** changed. `NetworkNodesOutro` was already
aspect-free — it reads `width`, `height`, `fps` and `durationInFrames` from
`useVideoConfig()` — so nothing in the component needed rewriting for 16:9.

Frame 120 of `Outro` rendered before and after the `Root.tsx` edit:

```bash
npx remotion still src/index.tsx Outro <out>.png --frame=120
```

```
d86ded35b2091ec65f03ba470832a04a034300f6042932fdf287a5519f914728  portrait-before-f120.png
d86ded35b2091ec65f03ba470832a04a034300f6042932fdf287a5519f914728  portrait-after-f120.png
```

Identical sha256 — the portrait output is pixel-identical. The `defaultProps` were also
diffed string by string against the previous file (all seven byte-identical, including the
em dash) after being lifted into the shared `OUTRO_DEFAULT_PROPS` constant.

## The 24 fps variant

Remotion's `fps` is a **composition** property, not a component prop, and the CLI has no fps
override, so 24 fps needs its own composition rather than a prop. `OutroLandscape24` is
1920x1080 at 24 fps with `durationInFrames` scaled: 186 x 24 / 30 = 148.8, rounded to **149**
(6.2083 s, 8 ms longer than the 6.2 s card — `authoring/audio.py`'s `OUTRO_S` constant is
unaffected, it is arithmetic on `t_vo_end`).

**One behavioural difference, not a bug but worth knowing.** `NetworkNodesOutro`'s closing
fade is written in *frames*, not seconds (`interpolate(frame, [durationInFrames - 25,
durationInFrames], [1, 0])`). 25 frames is 0.833 s at 30 fps and **1.042 s at 24 fps**, so the
24 fps card fades out ~0.2 s more slowly. Measured on the rendered files, mean luma of the
frame at t=5.70 s: **8.72** (30 fps) vs **6.66** (24 fps). Everything else in the component is
time-based (`t = frame / fps`, and `spring()` is given `fps`), so the entrance, the node drift
and the ember travel are identical in wall-clock terms. Making the fade time-based would
change the portrait card too, so it was left alone.

## Known, unchanged

`NetworkNodesOutro.tsx` has `CONNECTION_DISTANCE = 260` with the comment *"tuned for the
1080x1920 canvas (original 220 was set against 1920x1080)"*. It is a pixel distance, so at
1920 wide the constellation lines span relatively less of the frame than they do in portrait.
The rendered landscape frame was inspected and reads as the same starfield, so it was left at
260 rather than changing a constant the portrait card shares. If the operator wants the
denser landscape web the comment describes, the fix is an optional `connectionDistance` prop
defaulting to 260 — a separate, deliberate change.
