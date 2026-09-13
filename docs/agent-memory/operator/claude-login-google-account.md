---
name: claude-login-google-account
description: "The operator's Claude account with the subscription (incl. Claude Design) is the Google login; Edge (default browser) is signed into an old account with none"
metadata: 
  node_type: memory
  type: user
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-03T01:00:32.225Z
---

The operator has two Claude accounts. The one with the subscription — and
the only one with Claude Design access — is the **Google** login. Windows'
default browser is Microsoft Edge, which is signed into an **old** account,
so any `/login` or `/design-login` that opens Edge silently authenticates
the wrong account. Symptom (2026-09-02): DesignSync `list_projects`
succeeds but `create_project` returns `403 permission_denied: subscription
required for this action`.

**How to apply:** when an auth flow fails with a subscription/permission
403, ask which account the browser signed in before assuming the feature
is gated or removed. Recovery: `/logout`, `/login` with the URL pasted into
Chrome (Continue with Google), then `/design-login`. Never enter
credentials or complete sign-in on the operator's behalf.
See [money-physics-brand-sheet](money-physics-brand-sheet.md).

**2026-09-05 update:** the CLI (2.1.259) is logged in as sniperownage@gmail.com (Max) - `claude auth status` is the check, and `claude -p` from the repo root works for other lanes to commission Claude. The magolliet login on 2026-09-05 came from a CLI `/login` prompted by the Astra lane: the flow opened in the browser's default Google account; the operator signed out and back in and the CLI is clean (the desktop app's own login flow was never the problem). My 'Not logged in' probe ran in between. Rule: when another lane prompts a CLI login, paste the URL into the Chrome profile signed in as sniperownage. Never print the tokens.
