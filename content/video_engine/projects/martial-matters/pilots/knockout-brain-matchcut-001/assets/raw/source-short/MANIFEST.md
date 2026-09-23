# Knockout brain match-cut source manifest

Status: `review_only`; `render_eligible=false`; operator approval is required.
This is a custody and inspection packet, not a release or fair-use decision.

## Primary source records

### Supplied Short

- Source: `https://youtube.com/shorts/ID0sgoVzFNQ?si=MU3r0VLMpfC8VGyC`
- Canonical watch URL: `https://www.youtube.com/watch?v=ID0sgoVzFNQ`
- Observed channel/title: One Stop MMA / `Gable Steveson Gets Slept in 5 Seconds 😳 #ufc #mma`.
- Highest public format recovered from the format inventory: YouTube format `616`
  (1080x1920 VP9 video-only, 30 fps, Premium-labelled HLS rendition) plus
  format `251` Opus audio. The merged custody copy is
  `supplied-short-high.mkv`; the raw tracks are retained beside it.
- ffprobe: 1080x1920, VP9/Opus, 30 fps, 24.361 seconds, 13,004,205 bytes for
  the merged MKV. The exact JSON is `ffprobe-supplied-short-high.mkv.json`.
- Visual inspection places the Short's fight/knockdown action at approximately
  15.3-16.7 seconds of the 24.361-second Short. See the two focused contact
  sheets; this is an editorial window, not an adjudicated bout timestamp.
- Captions are preserved unmodified in `supplied-short-high.en-orig.vtt` and
  `supplied-short-high.en.vtt`. They say `Sean Sherriff` and `10 seconds`, and
  include an uncited personal allegation. These are publisher captions, not
  verified facts.

### Authoritative underlying-bout source

- Source page: `https://www.ufc.com/video/160276`
- UFC page title: `Sean Sharaf Knocks Steveson Out In 12 Seconds | Crypto.com UFC 331 | UFC`.
- The page's public DVE player metadata identifies DVE video `1020834`; the
  raw provider JSON is retained as `ufc-sharaf-steveson-provider.json`.
- The recovered official highlight is `ufc-sharaf-steveson-high.mkv`:
  1920x1080 H.264/AAC, 30 fps, 25.066 seconds, 22,405,698 bytes. The exact
  JSON is `ffprobe-ufc-sharaf-steveson-high.mkv.json`.
- Visual inspection places the highlight's knockout sequence at approximately
  1.1-2.8 seconds of the UFC clip. The official page identifies Sharaf, which
  reconciles the Short's incorrect `Sean Sherriff` caption.

## Artifact inventory

All rows are quarantined with `review_only=true` and `render_eligible=false`.
Full SHA-256 coverage for every file below (including contact sheets, probes,
captions, metadata, and watch outputs) is in `SHA256SUMS.txt`.

| Artifact | Purpose | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| `supplied-short-high.mkv` | Highest recovered Short, merged custody copy | 13004205 | `d06202a8606129c1888d18b870406f339e7b9fbcba5bcfeea0bd9389bf1f4fd7` |
| `supplied-short-high.f616.mp4` | Raw 1080x1920 YouTube VP9 video track | 12670809 | `28dcb35b6276aa6b62c17650ffa1268e92b23bd0dd38c25f66c702259dda260a` |
| `supplied-short-high.f251.webm` | Raw YouTube Opus audio track | 337255 | `64463d2248556a65e0b4e272cd1875fc5d9a98a66ee6d1baad57ecf59e69af45` |
| `supplied-short-high.info.json` | yt-dlp source metadata/format record | 599861 | `b299cb499025f847bd18608174ed32a2906a93b856c10620aa3bb40c0b20d78d` |
| `supplied-short-high.en-orig.vtt` | Original English captions | 2719 | `2dff9b82ee27692971c142f1500c0b18d2b54c134f2b9f9d925a29659c7e459e` |
| `supplied-short-high.en.vtt` | English auto-caption response | 2719 | `2dff9b82ee27692971c142f1500c0b18d2b54c134f2b9f9d925a29659c7e459e` |
| `ufc-sharaf-steveson-high.mkv` | Official UFC public highlight | 22405698 | `c162dcb7e7a11336c5b0bd3b29d51ecbf2f8cd5a49f90a3b851775165da64758` |
| `ufc-sharaf-steveson-high.info.json` | yt-dlp provider metadata record | 18453 | `e3b2e9670e46d413d7f69cad51bf0a74bab5a3c72164dc7f7f12f4e87d6364f0` |
| `ufc-sharaf-steveson-provider.json` | Raw public DVE provider response | 2309 | `85b6af6ecc5160eac3690aea02e0383d3fc02d58bd4bc826ca4783d352285b34` |
| `ufc-video-160276.html` | Raw UFC source page response | 99559 | `7de3f9177837fb3af328290ad3ac68a8b2f5a6a4bb08de9c862f7684dfb64811` |
| `COMMANDS.md` | Exact retrieval/probe commands | see hash record | see hash record |
| `receipt.json` | Machine-readable custody receipt | see hash record | see hash record |

The `watch-pass/` directory is retained as a lower-quality provenance pass:
yt-dlp's default watch download is 360x640 AV1/Opus, with the eight extracted
frames and duplicate VTT/info files. It is not the selected recovery ceiling.

## Limitations

- Public playback URLs issued by UFC's DVE endpoint are signed and expire under
  provider control; the raw response is preserved, but a later rerun may issue
  different tokens.
- The watch script downloaded successfully but exited while printing because
  Windows cp1252 could not encode the Short title emoji. This does not affect
  the separately recovered high-format files.
- The supplied Short's case language is not an adjudicated record. Preserve the
  captions as evidence of what the publisher said, not as a verified finding.
- No asset is approved, publication-ready, or eligible for rendering.
