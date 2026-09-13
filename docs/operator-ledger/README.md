# Operator ledger

Every message the operator typed into the Claude transcripts for this repo, **in the operator's own words, verbatim**,
with the agent's first reply after it (context, not a summary) and how many tool calls followed. Built by
`content/video_engine/scripts/extract_operator_ledger.py` (P54 T1). No tool output, subagent traffic, harness
messages, bridge packets or `/model` switches.

## Layers

- `LEDGER.jsonl` is the **evidence layer**. It is JSONL, so `docs_find` does not index it: a search never lands on a
  chat fragment. Grep it by id or phrase.
- The markdown is **on demand** only: `--md <path>` writes a day-grouped view (pasted rows cut to 200 characters).
  Write it outside `docs/`, and never commit it there.
- `TRIAGE.jsonl` holds one verdict per correction/rule row (P54 T2).

## Re-run

    python content/video_engine/scripts/extract_operator_ledger.py --check          # exit 1 when newer messages exist
    python content/video_engine/scripts/extract_operator_ledger.py                  # incremental (default): append rows newer than the last ts
    python content/video_engine/scripts/extract_operator_ledger.py --full           # rebuild from scratch
    python content/video_engine/scripts/extract_operator_ledger.py --md <path>      # also write the markdown view
    python content/video_engine/scripts/extract_operator_ledger.py --triage-check   # validate TRIAGE.jsonl

The same text again within 600 s of a kept row is dropped as a near-duplicate.

## Row schema (LEDGER.jsonl)

| field | meaning |
|---|---|
| `id` | first 12 hex of sha1(ts + text), stable across re-runs |
| `ts`, `session`, `cwd`, `file` | when, which session, where it was typed, the transcript's project folder |
| `text` | the operator's words, verbatim (system reminders stripped; for a slash command, the words after it) |
| `images` | images attached to the message |
| `via` | `typed`, `mid-turn` (queued while the agent worked) or `slash` |
| `slash` | the slash command's name when `via` is `slash` |
| `pasted` | a traceback, an `@"` paste or over 3,000 characters |
| `cues` | substring hints for triage: `correction`, `rule`, `approval`, `question`, `why` (not a classifier) |
| `reply` | the agent's first text after the message, 600 characters |
| `tool_calls` | tool calls the agent made before the operator's next message |

## Triage

Triage verdicts live in `TRIAGE.jsonl`, never in the ledger: rows `{id, ts, verdict, anchor, subject, note}`.
The verdict is one of `recorded`, `ruling-candidate`, `gate-candidate`, `craft`, `memory`, `episode`, `noise`,
`conflict` or `superseded`.
- A `recorded` anchor starts with an existing repo-relative path (`path` or `path:heading`).
- A `superseded` anchor names what overturned the correction: a later ledger row id or a ruling id such as `E73`. A
  superseded correction never reaches another agent as a live rule.

`--triage-check` requires exactly one verdict per non-pasted correction/rule row. **Only the operator makes a verdict
a ruling**: triage proposes; E-ids are written from the operator's words alone.
