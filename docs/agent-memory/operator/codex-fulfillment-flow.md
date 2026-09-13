---
name: codex-fulfillment-flow
description: "How image-generation claims get FULFILLED - codex exec headless (the CLI hides inside the ChatGPT Store app; copy 3 binaries out), then claim-resume. Never Chrome, never image APIs, never computer-use."
metadata: 
  node_type: memory
  type: project
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-13T05:43:55.658Z
---

Image generation runs on the operator's subscription agents via the
claims pipeline (doc 26, runbook docs/runbooks/HEADLESS_CLAIM_RESUME.md):

1. **Open a claim**: `open_claim(...)` from
   `content/video_engine/src/services/generation_claim.py` (mimic
   `scratchpad/open_steel_paper_claim.py`); render WORK-ORDER.md into the
   claim's delivery dir under `review/claims/<claim-id>/`.
2. **Fulfil headless**:
   `codex exec --cd "<delivery_dir>" --skip-git-repo-check --approve-for-me
   -c model_reasoning_effort="low"
   "Read and follow the work order at <path>\WORK-ORDER.md"`
   (`--approve-for-me` is required headless - without it the run parks on
   an approval prompt at 0 CPU forever; it cannot be combined with `-s`.
   Redirect stdin from /dev/null and stdout to a log file.)
3. **After delivery** (approvals.json written last):
   `python -m content.video_engine.cli claim-resume <claim-id>`.

**Finding codex on this machine (2026-08-31):** the CLI ships INSIDE the
ChatGPT desktop Store app - no PATH alias, invisible to which/Get-Command.
Location: `C:\Program Files\WindowsApps\OpenAI.Codex_<ver>_x64__2p2nqsd0c76g0\app\resources\`.
Copy FOUR binaries to a writable dir (they must sit together, codex
spawns the helpers beside itself): `codex.exe`,
`codex-code-mode-host.exe`, `codex-command-runner.exe`, and (since
0.151, 2026-09-03) `codex-windows-sandbox-setup.exe` - without it every
exec_command fails "orchestrator_helper_launch_failed ... program not
found" and the run idles. With only codex.exe it fails "code-mode host
not found". Version dir changes on app
updates - re-glob `OpenAI.Codex_*`. A copy lives in the session
scratchpad; re-copy fresh if stale.

**This is also THE Codex / Astra lane for any dispatch, not just images** (operator, 2026-09-13: *"Why do you think
Codex has no bridge lane? you know that it does."*). `viewer_run.py` (`DEFAULT_LANE = "codex"`) drives judging batches
the same way, and Astra already reviews packets back to Claude. `bridge_send.py`'s `LANES = ("gemini", "claude")` only
lists the two CLIs IT shells - never read one constant as "the bridge has no Codex lane". To hand Astra/Codex work:
`codex exec` headless with the brief's path.

**Never**: Chrome/claude-in-chrome, OpenAI image APIs, computer-use on
the GPT desktop window. The operator corrected all three in one session.
Related: [recall-system](recall-system.md).

**Prompt phrasing (operator, 2026-08-31):** describe the OBJECT, not
the treatment. "The word Memory, as if the word itself were physically
built out of memory chips" → real 3D construction from RAM sticks.
"Word-art / letterforms filled with chip texture" → flat wallpaper
fill ("reads like a quilt"). Name the physical thing the image IS.

**Vocabulary matters as much as object-vs-treatment:** "memory chips /
RAM sticks" → physically accurate BLACK packages (dark stripes at
thumb scale, three rejected rounds). What the eye means by
"electronics/semiconductors" is the ICONOGRAPHY: luminous green PCB +
shining gold traces + wafer sheen. When an image is dark and the ask
was vivid, ban the darkness explicitly ("if a letter reads mostly dark
at small size, it is wrong") - the winning round did exactly that.
