# The Remotion kit

The Remotion project the first reel's outro came from ("It's not magic. It's mechanics." on
the network-nodes field, `@MoneyPhysicsHQ`), plus the yen chart, the captions and the film
frame compositions built beside it. Rescued 2026-09-05 from a session scratchpad
(`youtube-video-review-e67e8f`, session `59b51626`, rendered 2026-09-02) - it had never been
committed, and the operator pointed at it: "we have the outro built already, same as we used
for the first reel ... it was the remotion kit outro".

| composition | file | what |
|---|---|---|
| `Outro` | `src/NetworkNodesOutro.tsx` via `src/Root.tsx` | 186 frames at 30 fps, 1080x1920: headline, tagline, handle pill, nodes that drift and pulse, embers |
| yen chart | `src/YenChart.tsx`, `src/chart-index.tsx`, `yen-evidence.json` | the first reel's chart |
| captions | `src/Captions.tsx`, `src/captions-index.tsx`, `captions-yen.json` | the first reel's word-timed captions |
| film frame | `src/FilmFrame.tsx`, `src/film-index.tsx` | the film-strip frame |

`package.json` is the bare scratchpad one (no dependencies declared): the kit rendered against
the editor's `node_modules` (`content/video_engine/editor/`). To render again, install there and run
`npx remotion render src/index.tsx Outro out/outro-brand.mov --codec prores` from this folder
with the editor's `node_modules` on the path, or add `remotion`, `react`, `react-dom` here first.

**The brand line** - "Not a panic. Not a plot. Mechanics." - is a CHANNEL asset recorded once (ElevenLabs, 2026-09-05,
request `VWz6F5nZII19oUXxsUYt`, 2.3 s, the take's own voice and settings) at
`content/video_engine/channel-assets/money-physics/outro/` (`BRAND-LINE.txt`, `vo/short-take.json`, `vo/audio/scene_1.words.json`;
the mp3 is gitignored like every take - it lives in that folder and its `vo/cache/`). `pace_brand_line.py` cuts it at its
own word gaps and gives each stroke a period's room (0.5 s after "panic.", 0.8 s before "Mechanics." - operator: "it reads
too fast"), writing `vo/audio/brand-line-paced.mp3` + its shifted word clock (3.58 s). Every short stitches THAT file 0.7 s
after its last word, under the card; the card's own text is its caption.

Renders are gitignored (`*.mov`, `*.png`). The four renders sit beside the Tokyo clips at
`projects/systems-and-blowups/tokyo-tea-break/outro/` (6.2 s each, ProRes, silent audio track): the short uses
`outro-v2.mov`, the dark card the operator showed; `outro-brand.mov` is the cream brand re-skin, `outro-yt.mov` says
"subscribe" for YouTube, `outro.mov` is the first reel's `@frmwrkd` card. `build_short.py` re-encodes the chosen one to a
seekable mp4 and DISSOLVES it in as the last word ends (exit `dissolve`).
