# Early free-provider portrait look — 2026-09-23

Status: **review-only UI observation**, not the T10 native/raw/cleaned benchmark, fighter-art approval, a local mesh audit, or a commercial-use determination. The operator authorized uploading this specific portrait to Tripo and Meshy for one free image-to-model test each. No purchase, subscription, terms acceptance, or publication occurred.

## Common input and limits

- `C:/Users/Snipe/.codex/wt/hl/content/video_engine/review/model-engines/benchmark-v1/art/target-concepts/sharaf-head-shoulders-concept-v2.png`; SHA-256 `43a1d76745143d6d7dcbab8231709781dd1f6dd5ea676dbe427e8224bcad106f`; 1,775,198 bytes. A stylized three-quarter **head-and-shoulders portrait**, not a full-body turnaround or A-pose. Both services received this same file.
- Comparisons below are of signed-in browser previews rotated to front and side/rear. Neither free output could be exported as GLB, so the saved mesh, UVs, riggability, deformation, material seams and import compatibility could not be independently inspected. The generated previews are not an approved native-art comparator.

| Observation | Tripo Studio | Meshy |
|---|---|---|
| Mode/model | Clean Topology free trial; Smart Mesh P2.0 | Smart Topology; Meshy T2; requested 4,000 poly; Texture on; Pose off; UI selected CC BY 4.0 |
| Generation cost observed | Trial button showed 100 struck through to 0; balance stayed 200 credits; trial count went from 2 to 1 | Button showed 15 credits; initial balance 100; provider automatically awarded 30 daily check-in credits, then balance showed 115 after generation, consistent with 15 spent |
| Result handle | `https://studio.tripo3d.ai/workspace/generate/66cbd792-04fa-475f-b1a4-62da7ece558c` | Signed-in `https://www.meshy.ai/workspace?model-tab=image-to-3d`; visible result thumbnail URL contained task ID `01a0cee0-f2c3-7019-9fb3-cc7d8eafa787` |
| Preview mesh readout | Quad topology; 6,355 faces, 5,332 vertices | Triangle topology; 4,274 faces, 3,557 vertices for textured result (the separate gray topology preview displayed 2,181 vertices) |
| Visible strengths | Recognizable bald head, brow, nose, ear and beard volumes; fairly coherent quad flow around head, shoulder/neck and visible back; much closer to the requested bust than a blockout | Immediate color/tattoo/clothing read; generated arms, hands, legs and rear where the source had no coverage; recognizable bald/bearded theme |
| Visible misses | Untextured on the free trial; spiky/faceted beard and eyes; only a bust with an open lower edge, no fighter body, hands or motion test | Fabricated squat full-body proportions and costume/body details absent from the input; flat facial likeness, mitten-like hands and conspicuous image-derived tattoo coverage; triangular mesh preview gives no deformation proof |
| Export check | GLB selected in Export dialog; final Export opened “Upgrade to export ready-to-use 3D assets” subscription prompt | GLB selected in Download Settings; Download opened “subscribe Pro for Unlimited model downloads” prompt |

No provider model file was downloaded or imported. Both signed-in comparison tabs were retained in the in-app browser for operator review. The Tripo preview is more promising as a **head-geometry starting point**; Meshy is a quick surface/style suggestion, but its invented body is not a usable fighter identity. This is an inference from the previews only. The free-tier export gates prevent testing either as a reusable rigged production asset. Keep the editable Blender character and motion work as the primary path. A paid/export trial, texture pass, rig test or second reference input requires a separately scoped decision; it is not implied by these observations.
