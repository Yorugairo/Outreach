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

Renders are gitignored (`*.mov`, `*.png`). The outro render the Tokyo short uses is
`projects/systems-and-blowups/tokyo-tea-break/outro/outro-brand.mov` (6.2 s, ProRes, silent
audio track); `build_short.py` re-encodes it to a seekable mp4 and appends it after the last word.
