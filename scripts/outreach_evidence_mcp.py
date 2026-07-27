from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.repositories.file_repository import FileBackedInsightRepository


def _repository(artifact_root: str) -> FileBackedInsightRepository:
    return FileBackedInsightRepository(Path(artifact_root))


def _load_pack(
    repo: FileBackedInsightRepository,
    run_id: str | None,
    evidence_pack_id: str | None,
    attempt_id: str | None,
) -> dict:
    if evidence_pack_id:
        pack = repo.get_site_evidence_pack(evidence_pack_id)
        if pack is None:
            raise RuntimeError(f"evidence pack not found: {evidence_pack_id}")
        if run_id and pack.run_id != run_id:
            raise RuntimeError("requested evidence pack does not belong to the scoped run")
        if attempt_id and pack.attempt_id != attempt_id:
            raise RuntimeError("requested evidence pack does not match the scoped attempt")
        return pack.to_dict()

    if not run_id:
        raise RuntimeError("either --pack-id or --run-id is required")

    candidates = [p.to_dict() for p in repo.list_site_evidence_packs(run_id=run_id)]
    if attempt_id:
        for pack in candidates:
            if pack.get("attempt_id") == attempt_id:
                return pack
        raise RuntimeError(
            f"no evidence pack found for run={run_id} and attempt={attempt_id}"
        )

    if not candidates:
        raise RuntimeError(f"no evidence pack found for run: {run_id}")
    return candidates[0]


def _emit_pack(repo: FileBackedInsightRepository, run_id: str | None, pack_id: str | None, attempt_id: str | None) -> None:
    pack = _load_pack(repo, run_id=run_id, evidence_pack_id=pack_id, attempt_id=attempt_id)
    print(json.dumps(pack, indent=2, sort_keys=True))


def _mcp_error(request_id, message: str) -> None:
    print(
        json.dumps(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32000, "message": message},
            }
        )
    )


def _mcp_serve(repo: FileBackedInsightRepository, run_id: str | None, pack_id: str | None, attempt_id: str | None) -> None:
    # Minimal JSON-RPC endpoint used by Hermes MCP integration.
    scope = {"run_id": run_id, "evidence_pack_id": pack_id, "attempt_id": attempt_id}
    tools = [
        {
            "name": "get_scoped_evidence_pack",
            "description": "Read-only access to the scoped SiteEvidencePack",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "evidence_pack_id": {"type": "string"},
                    "attempt_id": {"type": "string"},
                },
                "additionalProperties": False,
            },
        }
    ]

    for raw in sys.stdin:
        line = raw.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        req_id = payload.get("id")
        method = payload.get("method", "")
        params = payload.get("params", {}) if isinstance(payload.get("params"), dict) else {}

        if method == "initialize":
            print(
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "serverInfo": {"name": "outreach-evidence-mcp", "version": "0.1"},
                            "capabilities": {"tools": {"listChanged": False}},
                        },
                    }
                )
            )
            continue

        if method == "tools/list":
            print(
                json.dumps(
                    {"jsonrpc": "2.0", "id": req_id, "result": {"tools": tools}},
                )
            )
            continue

        if method == "tools/call":
            tool_name = params.get("name")
            if tool_name != "get_scoped_evidence_pack":
                _mcp_error(req_id, "tool not allowed")
                continue
            requested_pack = params.get("arguments", {}).get("evidence_pack_id") if isinstance(params.get("arguments"), dict) else None
            requested_attempt = params.get("arguments", {}).get("attempt_id") if isinstance(params.get("arguments"), dict) else None
            scoped_pack_id = scope["evidence_pack_id"]
            if requested_pack and scope["evidence_pack_id"] and requested_pack != scoped_pack_id:
                _mcp_error(req_id, "arbitrary pack ids are not allowed")
                continue
            if requested_attempt and scope["attempt_id"] and requested_attempt != scope["attempt_id"]:
                _mcp_error(req_id, "attempt id out of scope")
                continue
            try:
                pack = _load_pack(
                    repo,
                    run_id=scope["run_id"],
                    evidence_pack_id=scoped_pack_id or requested_pack,
                    attempt_id=requested_attempt or scope["attempt_id"],
                )
                print(
                    json.dumps(
                        {
                            "jsonrpc": "2.0",
                            "id": req_id,
                            "result": {"content": [{"type": "text", "text": json.dumps(pack)}]},
                        }
                    )
                )
            except RuntimeError as exc:
                _mcp_error(req_id, str(exc))
            continue

        _mcp_error(req_id, "method not supported")


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only MCP bridge for scoped evidence packs")
    parser.add_argument("--artifact-root", default=str(ROOT_DIR / "artifacts" / "seo_insight_runs"))
    parser.add_argument("--run-id", help="Scope tool to one run")
    parser.add_argument("--pack-id", help="Scope tool to one evidence pack")
    parser.add_argument("--attempt-id", help="Optional scoped attempt_id")
    parser.add_argument("command", nargs="?", choices=["get", "serve"], default="get")

    args = parser.parse_args()
    if not args.run_id and not args.pack_id:
        raise SystemExit("either --run-id or --pack-id is required")

    repo = _repository(args.artifact_root)

    if args.command == "serve":
        _mcp_serve(repo, args.run_id, args.pack_id, args.attempt_id)
        return 0

    _emit_pack(repo, args.run_id, args.pack_id, args.attempt_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
