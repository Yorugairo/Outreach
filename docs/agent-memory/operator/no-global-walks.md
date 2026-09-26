---
name: no-global-walks
description: "never walk the home directory or C: recursively (Get-ChildItem -Recurse / find / hashing everything); 09-24 a whole-home disk audit + the operator's recycle-bin empty starved the machine into a restart - scope every search to named folders; agent concurrency is NOT the problem, don't cap it"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-25T04:37:52.898Z
---

2026-09-24 ~21:00: I dispatched a "disk audit" that walked all of `C:/Users/Snipe` recursively and hashed every >=1 MB file across all worktrees. With the operator emptying a huge recycle bin at the same time, disk IO starved: Hermes's log shows DNS lookups failing (21:02), a tiny Temp write taking 65 s (21:08), API/Telegram timeouts (21:13); the operator restarted at 21:23 (no bugcheck, no app crash logged). The operator: "the issue was probably my recycling bin empty + you having an undisciplined global walk, we've had documented issues with global walks before".

**Why:** a recursive walk over millions of files (node_modules, Temp, caches, worktrees) saturates disk IO and PowerShell holds every object in memory; it hurts every process on the machine, not just the walker.

**How to apply:** never `Get-ChildItem -Recurse`, `find`, `du`, `rg` or a hash pass over `C:\`, the home directory, `AppData`, `Temp` or "all worktrees" at once. Scope to NAMED folders; for sizes use `robocopy <dir> NUL /L /S /NJH /BYTES /NFL /NDL` (summary only) one folder at a time; hash only files whose SIZES already collide, within named dirs. A disk audit is a sequence of small bounded measurements, never one global walk. Do NOT cap the number of agents - the operator ran many in parallel before without trouble; I wrongly proposed a two-renderer cap. Related: [scratch-trees-die-on-commit](scratch-trees-die-on-commit.md), [worktree-read-scope](worktree-read-scope.md).
