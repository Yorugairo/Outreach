# Henderson–Bisping UFC 100 recovery manifest

Status: review_only / render_eligible=false.

## Source and custody

- Official UFC page: https://www.ufc.com/video/49967
- Resolved public media URL recorded by yt-dlp: https://ufc.com/images/2016/04/11/KOTW-hendo.dsk.mp4?VersionId=FxFmrDFxJm6tQoi994OlDrSjgnzuLmXd
- Retrieval policy: public unauthenticated HTTP only. No cookies, account access, paywall bypass, or DRM circumvention.
- Exact commands: [retrieval-command.txt](retrieval-command.txt)
- Original media: [ufc-49967-henderson-bisping-official.mp4](ufc-49967-henderson-bisping-official.mp4)
- Source metadata: [ufc-49967-henderson-bisping-official.info.json](ufc-49967-henderson-bisping-official.info.json)
- Public format inventory: [format-inventory.txt](format-inventory.txt)
- Independent probe: [ffprobe.json](ffprobe.json)
- Hash record: [SHA256SUMS.txt](SHA256SUMS.txt)

## Recovered quality

The official UFC page exposed one direct MP4 rendition; yt-dlp's public format inventory is preserved in format-inventory.txt. The preserved original is 854x480 progressive H.264/AVC Main at 29.97 fps (2997/100), 75.241909 s video duration, with stereo AAC-LC 44.1 kHz audio. No higher-resolution official UFC rendition was exposed by the page's public HTML5 media source during this recovery; this is the verified public quality ceiling for this source, not an upscale.

The file includes broadcast title/partner lower-thirds and intermittent transitions. Those graphics remain visible in the contact sheets and are not removed from the original.

## Match-cut windows

Timestamps are source-file seconds and are safe editorial windows, not claims of a single exact contact pixel. The labeled sheets are 5 fps review probes; select the final cut after operator review.

| Window | Source range | Knockout action / cut note | Contact sheet |
| --- | ---: | --- | --- |
| Primary clean KO | 31.8-35.9 s | Wide setup into Henderson's right, Bisping's fall, overhead follow-through; punch contact is approximately 32.7-32.9 s. | [primary-29.5-36.5.jpg](contact_sheets/primary-29.5-36.5.jpg) |
| Replay 1 | 46.0-50.8 s | Side replay; contact/fall sequence approximately 47.5-50.3 s, with the clearest readable head/hand relationship around 47.7-48.3 s. | [replay-1-45.5-50.8.jpg](contact_sheets/replay-1-45.5-50.8.jpg) |
| Replay 2 | 51.0-58.8 s | Second angle; setup, punch, collapse, and floor aftermath; use approximately 52.6-57.8 s for the action and 58.0-58.8 s for the floor hold. | [replay-2-51.0-58.5.jpg](contact_sheets/replay-2-51.0-58.5.jpg) |

Supporting watch evidence remains under [watch-impact](watch-impact/) and [watch-replay](watch-replay/), with their reports and 3-tile sheets.

## Review contract

- approved: unset; operator decision required.
- review_only: true.
- render_eligible: false.
- The original MP4 is immutable custody evidence. Derived frames/contact sheets are inspection aids only and do not replace the original.
- Rights/licensing status is not asserted by this recovery. UFC attribution is preserved; publication requires the parent/operator's rights and editorial decision.
