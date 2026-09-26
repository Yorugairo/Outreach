---
name: sec-fetch-user-agent
description: research agents fetching SEC EDGAR must use a generic contact User-Agent, never the operator's email - R26-306 sent it once (2026-09-24)
metadata:
  type: feedback
---

SEC EDGAR asks for a contact in the User-Agent header. On 2026-09-24 the R26-306 research agent's first curl to sec.gov carried the operator's email; later requests used a generic one. The operator's email is for identifying them only, never for a third-party request.

**Why:** the harness rule - the user's email is never sent to an unrelated service in a header, URL or payload unless they ask.

**How to apply:** every research brief that may fetch SEC / EDGAR / any site that asks for a contact states: use `User-Agent: MoneyPhysics-research research@localhost` (or the repo's configured agent contact), never the operator's email. Related: [research-gate-tiers](research-gate-tiers.md).
