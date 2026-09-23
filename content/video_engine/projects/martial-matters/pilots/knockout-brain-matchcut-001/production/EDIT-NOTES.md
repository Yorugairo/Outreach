# Sean Sharaf / One Punch replay

Review cut, 24.6 seconds, 9:16. Source modules are 30 fps; final engine export is 1080x1920 at 24 fps. Not uploaded.

Title: Sean Sharaf Goes One Punch Mode

## Edit

| Time | Picture and purpose |
|---|---|
| 0.0–3.5 | Sean celebration, “10 SECONDS.” hook and fresh narration |
| 3.5–8.1 | Sean's press-conference statement, visibly attributed; contemporaneous case outcome remains visible throughout |
| 8.1–11.6 | First real-time knockout |
| 11.6–12.9 | Anticipation pause and replay cue |
| 12.9–14.1 | Aura / anime transformation in matched pose |
| 14.1–14.8 | Return to the real punch |
| 14.8–17.8 | Blender head/brain recoil, stylized visualization |
| 17.8–22.0 | Dan Henderson knocking out Michael Bisping |
| 22.0–24.6 | Henderson replay |

## Sources and wording

- Promotional “10 seconds” follows the user's editorial instruction. UFC's published result is 0:12 of round one: https://www.ufc.com/video/160276 . This cut does not claim a universal start delay.
- Supplied reference and press excerpt: https://youtube.com/shorts/ID0sgoVzFNQ . Sean's spoken accusation is quoted news footage, not the narrator's factual assertion.
- Case outcome: Hennepin County Attorney, December 20, 2019, no charges filed following investigation. https://www.hennepinattorney.org/news/news/2019/December/university-wrestlers-12-20-2019 . See the recovered research/case/ source bundle for the full record and limits.
- Henderson–Bisping footage: https://www.ufc.com/video/49967 . Native recovered source is 854x480; portrait output does not add source detail.
- One Punch Man transformation: generated image edit of the exact pre-punch frame, then deterministic animated flash/zoom. It is a brief stylized insert, not a continuous character replacement across the live fight.
- Blender sequence illustrates stylized head/brain motion; it is not a medical reconstruction or diagnosis of either fighter.

## Rebuild

1. Run production/prepare_media.py to generate the selected portrait footage windows and anime effect.
2. Render production/blender/ using its included build script.
3. Generate production/audio/master.wav using its included audio build script.
4. Run the production/assembly/ builder against production/edit.json, then its existing-engine render command.

All original recovery artifacts are preserved. This folder contains derivatives and editable production code.
