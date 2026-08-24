"""Generation claims: work orders for subscription-agent image generation.

A claim is one batch of generation work, bound to one project root and one
style family. It owns a delivery directory (``review/claims/<id>`` — in-flight
class, per the P18 contract) and compiles a **work order**: a self-contained
document a generating agent (Codex headless, GPT desktop, Antigravity) follows
to generate, extract, self-judge and deliver. The staging and caps encode what
the v1/v2 probes proved:

- generation cannot produce native alpha → extraction is a distinct stage;
- the raw source render is the irreplaceable artifact → sources always ship;
- self-judgment is calibrated but bounded → 2 extraction attempts per slot,
  then the slot ships ``unresolved`` rather than looping.

The registry lives **outside every repo** at ``~/.video-engine/claims`` (env
override ``VIDEO_ENGINE_CLAIMS_DIR``) because a claim tracks machine state —
one operator generating one batch — and must survive branch switches and
worktree churn.

Git is consulted through one module-level boundary (``_run_git``) that tests
monkeypatch.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from content.video_engine.src.services import paths as _paths

ENV_CLAIMS_DIR = "VIDEO_ENGINE_CLAIMS_DIR"
DEFAULT_CLAIMS_DIR = Path.home() / ".video-engine" / "claims"

#: Probe-derived caps: best-of-N at generation, bounded retries at extraction.
GENERATION_CANDIDATES = 3
EXTRACTION_ATTEMPT_CAP = 2

#: Invocation economics (P17): mechanical orchestration needs no deep model.
DEFAULT_MODEL_EFFORT = "low"

_CLAIM_ID = re.compile(r"^[a-z0-9][a-z0-9-]{2,63}$")
_ASSET_ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")


class GenerationClaimError(Exception):
    def __init__(self, errors: Sequence[str]):
        self.errors = list(errors)
        super().__init__("; ".join(self.errors))


def _run_git(args: Sequence[str], cwd: Path) -> str:
    """The single git boundary; tests monkeypatch this."""

    result = subprocess.run(
        ["git", *args], cwd=str(cwd), capture_output=True, text=True, timeout=15,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def claims_dir(env: Mapping[str, str] | None = None) -> Path:
    source = os.environ if env is None else env
    override = source.get(ENV_CLAIMS_DIR)
    return Path(override) if override else DEFAULT_CLAIMS_DIR


def _claim_file(claim_id: str, env: Mapping[str, str] | None) -> Path:
    return claims_dir(env) / f"{claim_id}.json"


def _validate_slots(slots: Sequence[Mapping[str, Any]]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    if not slots:
        errors.append("a claim needs at least one slot")
    for index, slot in enumerate(slots):
        asset_id = str(slot.get("asset_id") or "")
        if not _ASSET_ID.match(asset_id):
            errors.append(f"slots[{index}].asset_id {asset_id!r} is not a valid id")
        elif asset_id in seen:
            errors.append(f"slots[{index}].asset_id {asset_id!r} appears twice")
        seen.add(asset_id)
        if not str(slot.get("prompt") or "").strip():
            errors.append(f"slots[{index}] ({asset_id or index}) has no prompt")
        if not str(slot.get("kind") or "").strip():
            errors.append(f"slots[{index}] ({asset_id or index}) has no kind")
    return errors


def open_claim(
    project_root: str | Path,
    *,
    claim_id: str,
    style_family: str,
    slots: Sequence[Mapping[str, Any]],
    reference_images: Sequence[str] = (),
    model: str | None = None,
    model_effort: str = DEFAULT_MODEL_EFFORT,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Open a claim: registry entry plus its review-class delivery directory."""

    errors: list[str] = []
    root = Path(project_root).expanduser().resolve()
    if not root.is_dir():
        errors.append(f"project root {root} is not a directory")
    if not _CLAIM_ID.match(claim_id):
        errors.append(f"claim id {claim_id!r} must be lowercase kebab, 3-64 chars")
    if not str(style_family or "").strip():
        errors.append("style_family is required — the mixing guard depends on it")
    errors.extend(_validate_slots(slots))
    for reference in reference_images:
        if not Path(reference).exists():
            errors.append(f"reference image {reference!r} does not exist")
    if errors:
        raise GenerationClaimError(errors)

    record_file = _claim_file(claim_id, env)
    if record_file.exists():
        raise GenerationClaimError([f"claim {claim_id!r} already exists; close it or pick a new id"])

    delivery_dir = _paths.review_dir(root, "claims", claim_id, ensure=True)
    claim = {
        "schema_version": "generation_claim.v1",
        "claim_id": claim_id,
        "status": "open",
        "project_root": str(root),
        "branch": _run_git(["rev-parse", "--abbrev-ref", "HEAD"], root),
        "style_family": str(style_family),
        "delivery_dir": str(delivery_dir),
        "slots": [dict(slot) for slot in slots],
        "reference_images": [str(Path(r).resolve()) for r in reference_images],
        "model": model,
        "model_effort": model_effort,
        "opened_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    record_file.parent.mkdir(parents=True, exist_ok=True)
    record_file.write_text(json.dumps(claim, indent=2), encoding="utf-8")
    return claim


def load_claim(claim_id: str, env: Mapping[str, str] | None = None) -> dict[str, Any]:
    record_file = _claim_file(claim_id, env)
    if not record_file.exists():
        raise GenerationClaimError([f"no claim {claim_id!r} in {claims_dir(env)}"])
    return json.loads(record_file.read_text(encoding="utf-8"))


def list_claims(env: Mapping[str, str] | None = None) -> list[dict[str, Any]]:
    directory = claims_dir(env)
    if not directory.is_dir():
        return []
    claims = [
        json.loads(f.read_text(encoding="utf-8")) for f in sorted(directory.glob("*.json"))
    ]
    return sorted(claims, key=lambda c: (c.get("status") != "open", c.get("opened_at", "")))


def close_claim(claim_id: str, env: Mapping[str, str] | None = None) -> dict[str, Any]:
    claim = load_claim(claim_id, env)
    claim["status"] = "closed"
    claim["closed_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    _claim_file(claim_id, env).write_text(json.dumps(claim, indent=2), encoding="utf-8")
    return claim


def verify_claim_matches_worktree(
    claim: Mapping[str, Any], project_root: str | Path
) -> list[str]:
    """Promote-time check: the claim's world must be the current one.

    Capturing into the wrong delivery is recoverable; promoting into the wrong
    catalogue is not — so the strict check sits here, not at capture.
    """

    errors: list[str] = []
    root = Path(project_root).expanduser().resolve()
    claimed_root = Path(str(claim.get("project_root") or "")).resolve()
    if claimed_root != root:
        errors.append(
            f"claim {claim.get('claim_id')!r} belongs to {claimed_root}, "
            f"but the console is serving {root}"
        )
    recorded_branch = str(claim.get("branch") or "")
    current_branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], root)
    if recorded_branch and current_branch and recorded_branch != current_branch:
        errors.append(
            f"claim {claim.get('claim_id')!r} was opened on branch "
            f"{recorded_branch!r}; the worktree is now on {current_branch!r}"
        )
    return errors


def claim_for_delivery(
    delivery: str | Path, env: Mapping[str, str] | None = None
) -> dict[str, Any] | None:
    """The claim owning a delivery directory, if any. None means unclaimed."""

    resolved = Path(delivery).resolve()
    for claim in list_claims(env):
        if Path(claim.get("delivery_dir", "")).resolve() == resolved:
            return claim
    return None


def render_work_order(claim: Mapping[str, Any]) -> str:
    """One self-contained document the generating agent can follow alone."""

    delivery = Path(str(claim["delivery_dir"]))
    slots = list(claim.get("slots") or [])
    manifest_assets = [
        {
            "asset_id": s["asset_id"],
            "path": f"objects/{s['asset_id']}.png",
            "sha256": "<lowercase hex sha256 of the delivered file bytes>",
            "kind": s.get("kind", "prop"),
            "semantic": s.get("semantic", ""),
            "source": {
                "path": f"source/{s['asset_id']}-source.png",
                "sha256": "<lowercase hex sha256>",
            },
        }
        for s in slots
    ]
    manifest = {
        "schema_version": "review_manifest.v1",
        "status": "review_only",
        "render_eligible": False,
        "style_family": claim["style_family"],
        "source_prompt": f"claim:{claim['claim_id']}",
        "assets": manifest_assets,
    }
    references = list(claim.get("reference_images") or [])
    reference_block = (
        "\n".join(f"- `{r}`" for r in references)
        if references
        else "- none supplied — follow the prompt text alone"
    )
    slot_blocks = "\n".join(
        f"### {s['asset_id']}  ({s.get('kind', 'prop')})\n\n{str(s['prompt']).strip()}\n"
        for s in slots
    )
    return f"""# Work Order — claim `{claim['claim_id']}`

Follow this document exactly. It is self-contained: generate, extract,
self-judge, deliver. Style family: `{claim['style_family']}`.

## Reference images (read-only inputs)

Pass these to your image generator as reference/conditioning inputs. Never
write into their directories.

{reference_block}

## Stage A — Generate (best-of, opaque allowed)

For each subject below, generate up to {GENERATION_CANDIDATES} candidates and
keep the best. A single flat solid pale ground is expected — no gradient, no
vignette, no dark backdrop; do not attempt transparency at generation time.
The full subject must have clear margin on all four sides — edge contact is an
automatic regeneration. Save each chosen original as
`source/<asset_id>-source.png` under the delivery folder.

{slot_blocks}

## Stage B — Extract

Matte each chosen source to a true-alpha cutout (rembg or equivalent), trim to
the subject's bounding box, pad onto a square transparent canvas with ~5%
margin, and save as `objects/<asset_id>.png`.

## Stage C — Self-judge the cutout (max {EXTRACTION_ATTEMPT_CAP} extraction attempts per slot)

1. Alpha is genuine — inspect the channel; full 0-255 range, subject opaque.
2. No halo: zoom the edge over a dark and a light ground — a rim in the
   *background's* colour is the failure; the subject's own soft edge is fine.
3. Nothing of the subject was eaten by the matte (thin parts, interior holes).
4. The source honours its prompt: one subject, stated palette and lighting,
   no text or numerals anywhere.

If extraction fails {EXTRACTION_ATTEMPT_CAP} times on a good source, **deliver
the source anyway** and list the cutout under `unresolved` — a delivered
source is recoverable; a withheld one is not.

## Stage D — Deliver

Delivery folder (create subfolders as needed):

    {delivery}

Write `{claim['claim_id']}.manifest.json` in the delivery folder:

```json
{json.dumps(manifest, indent=2)}
```

Compute every sha256 from the delivered file's bytes (PowerShell:
`Get-FileHash -Algorithm SHA256 <file>`; lowercase the hex).

Write `approvals.json` **last** — it is the completion signal:

```json
{{
  "judge": "<agent name and model>",
  "generation_attempts": {{"<asset_id>": 1}},
  "extraction_attempts": {{"<asset_id>": 1}},
  "approved": ["<asset_id>", "..."],
  "unresolved": [],
  "notes": "<one line per rejected attempt, if any>"
}}
```

The engine's deterministic scan verifies every hash and measures every alpha
rim independently — your approval is the first gate, not the last.
"""
