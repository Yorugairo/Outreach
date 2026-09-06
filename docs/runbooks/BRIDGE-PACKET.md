# The bridge packet — one shape for Claude, Gemini and Astra (P46 T4, draft for Astra's review)

An order between lanes is **a file and a send**. Nobody polls a folder for orders; the sender emits the packet through the
addressee's own CLI, and the packet file is the durable record. This page fixes the shape so the three lanes stop re-deriving it.
It adopts Astra's observed packet (six inbound sessions on 2026-09-05) and adds the fields the Claude → Gemini round trip of
2026-09-06 needed.

## 1. The packet (`order.json`)

| field | required | meaning |
| --- | --- | --- |
| `packetId` | yes | sha256 of the UTF-8 `brief`; the folder name under `docs/research/runs/bridge/<state>/` |
| `lane` | yes | `gemini` \| `claude` \| `astra` — the addressee |
| `from` | yes | the sending lane |
| `title` | yes | ≤ 80 chars; the conversation title on the addressee's side (how the conversation id is recovered) |
| `brief` | yes | Markdown, **≤ 6 KB**; the order itself; must name the repo root as an absolute path, the paths it may write, and the validation command |
| `replyShape` | yes | `paths-written` \| `contract-block` \| `report-landed` \| `review` \| `test-run` \| `free` — decides the tier-0 handler (§4) |
| `existingEvidence` | when relevant | the output of `docs_find.py "<topic>"` pasted in, so the addressee reads our sections before searching (GEMINI.md intake, step 6) |
| `deadline` | yes | ISO time; past it the watcher records `timeout` and the daemon escalates |
| `reviewOnly` | default false | true = the addressee reads and replies, writes nothing (Astra's alignment briefs) |
| `createdAt`, `sentAt`, `conversationId` | filled by the sender | provenance; `conversationId` is the addressee's handle for `send-message` / `--resume` |

Size caps are hard: a brief over 6 KB is split into two packets or points at a file by absolute path.

**An order names its skills** (operator, 2026-09-06, after the first live order came back wrong): the addressee has a
skills folder (`.agents/skills/`) it will not open on its own. Write *"use the `/watch` skill on <file>"*, or when the
skill is not known, *"choose your best skills for <the job> and name the ones you used"* - never just the verb. The Wealth
Logic cut classification went out as "classify from the video" with the `watch` skill (download, scene-aware frames,
transcript) sitting unused beside the profile, and came back as "all 99 hard cuts", which two frames refuted.

## 2. The reply grammar

Every reply, whatever the lane, opens with one of these lines and keeps the order:

```
POSITION: done | conditional | blocked
PATHS WRITTEN: <absolute path> ... (or none)
DISAGREEMENTS: - ... (or none)
PREREQUISITES: - ... (or none)
NOT FOUND WHERE I LOOKED: <roots and sources searched, coverage limits> (or none)
```

then free text. "Does not exist" is never a valid claim; "not found in <roots>" is. A reply that names a path the sender cannot
find on disk is `conditional`, not `done`. Replies are ≤ 250 words unless the order raises the cap.

## 3. The lanes

| lane | how a packet reaches it | where its reply appears |
| --- | --- | --- |
| Gemini (Antigravity) | `~/.gemini/antigravity-cli/bin/agentapi.bat new-conversation --model=pro [--profile] --title "<title>" "<brief>"` with `ANTIGRAVITY_LS_ADDRESS` (the language server's gRPC port), `ANTIGRAVITY_CSRF_TOKEN` (from its process command line, never written anywhere), `ANTIGRAVITY_PROJECT_ID` = the repo path; the repo must be in `~/.gemini/trustedFolders.json` | `~/.gemini/antigravity/brain/<conversationId>/.system_generated/logs/transcript.jsonl` — the last `PLANNER_RESPONSE` with content; continue with `send-message <id> "<text>"` |
| Claude | `claude -p --output-format json [--agent <role>] "<packet json>"` from the repo root; the reply is the run's result | the run's transcript under `~/.claude/projects/<cwd-slug>/`; a repeat message opens a new run (continuation is CLI `--resume`) |
| Astra / Codex | its own runner consumes packets from its queue folder (P2 T5) — documented here, not driven from this lane | its result record (P2's result schema); the Claude lane reads it from the packet folder when the runner writes it back |

## 4. What happens when a reply lands (P46 T6)

`replied/<packetId>/reply.md` is written by the watcher. Then, in order: **tier 0** — the deterministic handler for the
packet's `replyShape` runs (paths exist, block present at source and copies, report indexed and layers green, review grammar
parses without disagreements, test command exits 0) and closes the packet to `done/` with `tier: 0` in the ledger; **tier 1** —
only a reply tier 0 cannot close goes to the addressee-side judgment role (`bridge_handler` on the Claude side: verify against
disk, decide done / follow-up / escalate, write `result.md`); **escalation** — a packet still open past the SLA raises one desktop
toast to the operator. A live session sees `N bridge replies waiting` on its next prompt at no cost. Nobody is ever told to
"check the bridge".

## 5. The ledger

`evals/BRIDGE-LOG.jsonl` (per machine, gitignored): one line per event — `sent`, `replied`, `tier0`, `tier1`, `timeout`,
`escalated` — with `lane`, `packetId`, `conversationId`, seconds since `sentAt`, usage where the transcript exposes it (null
otherwise). The escape rate (tier 1 ÷ replied) is the number that decides whether the residue role stays on Opus.

## 6. Open for Astra's review (sent through the bridge as a `review` packet)

1. Field names: match P2's execution-order schema where one exists (`packetId` vs P2's run/task ids; `replyShape` vs P2's return schema).
2. The 6 KB cap and the 250-word reply cap — P2's limits are 12,000 input / 1,500 output tokens per retrieval trial; this page is for orders, not trials. Reconcile or keep both.
3. Whether Astra's runner will read `docs/research/runs/bridge/queue/` for packets addressed to it, or wants them delivered another way.
