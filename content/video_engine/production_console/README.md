# Remotion Production Console

Local, loopback-only operator surface for the current-bubble Remotion workflow.
Gate A is intentionally read-only: scene and asset selection affect only the
browser preview, while script, claims, timing, evidence state, source media, and
prior approvals remain protected.

The browser receives stable `/media/<asset-id>` URLs. It never receives local
filesystem paths. The same `ProductionEvidenceComposition` is used by the Player
and registered in the deterministic Remotion editor.

```powershell
npm ci
npm run typecheck
npm run test
npm run build
```

Start the Python bridge on `127.0.0.1:4317`, then run `npm run dev`. The Vite
server is also fixed to loopback and proxies `/api` and `/media` to the bridge.
