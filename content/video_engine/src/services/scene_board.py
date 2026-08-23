"""Three-tier scene board: resources, image candidates, video slots.

A 22-minute episode slots to roughly 150 plates. A one-of-three manual pick
across that many slots would be 150 operator decisions per episode, which
contradicts the minimize-human-in-the-loop goal outright. So the board
**auto-selects a default per slot and surfaces exceptions only**, sorted to the
top with their reason shown — the graduated-autonomy model already adopted
elsewhere in these docs.

The page is static and offline: relative image paths, inline CSS, no network.
Tier 3 renders one video slot per selected image in a visibly disabled state;
no provider is called and no paid job is released.
"""

from __future__ import annotations

import html
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

from content.video_engine.src.services.artifact_io import (
    artifact_hash,
    load_json,
    stamp_artifact_hash,
    write_artifact,
)

SCENE_BOARD_VERSION = "scene_board.v1"

_LOW_CONFIDENCE_THRESHOLD = 0.6
_EXCEPTION_REASONS = {
    "identity_anchor_violation": "Identity anchor violated — costume or silhouette drifted",
    "suspected_generated_text": "Suspected generated text in the plate",
    "low_confidence": "Low generator confidence",
    "near_duplicate_neighbour": "Near-duplicate of the adjacent slot",
    "no_candidate": "No usable candidate for this slot",
}


class SceneBoardError(ValueError):
    """The board could not be assembled from the supplied artifacts."""

    def __init__(self, errors: Sequence[str]):
        self.errors = [str(item) for item in errors]
        super().__init__("; ".join(self.errors) or "invalid scene board")


def _bound_hash(payload: Mapping[str, Any]) -> str:
    """Use the stamped hash, or derive one from content.

    A run agent may return a candidate batch without stamping ``artifact_hash``.
    Deriving it keeps the downstream selection review bound to the exact batch
    that produced the board instead of binding to nothing.
    """

    existing = payload.get("artifact_hash")
    return str(existing) if existing else artifact_hash(payload)


def _candidates_by_slot(items: Sequence[Mapping[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        slot_id = str(item.get("slot_id") or "")
        if slot_id:
            grouped[slot_id].append(dict(item))
    for candidates in grouped.values():
        candidates.sort(key=lambda entry: int(entry.get("variant_index") or 0))
    return grouped


def _auto_select(candidates: Sequence[Mapping[str, Any]]) -> dict[str, Any] | None:
    """Deterministic default: operator-selected, else lowest clean variant."""

    usable = [item for item in candidates if item.get("review_status") != "rejected"]
    if not usable:
        return None
    chosen = next((item for item in usable if item.get("review_status") == "selected"), None)
    if chosen is not None:
        return dict(chosen)
    clean = [item for item in usable if not list(item.get("qc_flags") or [])]
    pool = clean or usable
    return dict(min(pool, key=lambda entry: int(entry.get("variant_index") or 0)))


def _candidate_exceptions(candidate: Mapping[str, Any] | None) -> list[str]:
    if candidate is None:
        return ["no_candidate"]
    reasons = [flag for flag in (candidate.get("qc_flags") or []) if flag in _EXCEPTION_REASONS]
    confidence = candidate.get("confidence")
    if isinstance(confidence, (int, float)) and confidence < _LOW_CONFIDENCE_THRESHOLD:
        reasons.append("low_confidence")
    return sorted(set(reasons))


def _mark_near_duplicates(rows: list[dict[str, Any]]) -> None:
    """Flag a slot whose default shares a digest with the previous slot's."""

    previous: str | None = None
    for row in rows:
        digest = (row.get("selected") or {}).get("sha256")
        if digest and digest == previous:
            row["exceptions"] = sorted(set(row["exceptions"] + ["near_duplicate_neighbour"]))
        previous = digest or previous


def build_board(
    *,
    coverage: Mapping[str, Any] | str | Path,
    pack: Mapping[str, Any] | str | Path,
    batch: Mapping[str, Any] | str | Path,
    brief: Mapping[str, Any] | str | Path,
    attestation: Mapping[str, Any] | str | Path,
) -> dict[str, Any]:
    """Assemble the board payload with defaults already applied."""

    coverage_payload = load_json(coverage, "coverage")
    pack_payload = load_json(pack, "visual prompt pack")
    batch_payload = load_json(batch, "candidate batch")
    brief_payload = load_json(brief, "director brief")
    attestation_payload = load_json(attestation, "source attestation")

    grouped = _candidates_by_slot(batch_payload.get("items") or [])
    slots = list(coverage_payload.get("slots") or [])
    if not slots:
        raise SceneBoardError(["coverage contains no slots"])

    rows: list[dict[str, Any]] = []
    for slot in slots:
        slot_id = str(slot.get("slot_id"))
        candidates = grouped.get(slot_id, [])
        selected = _auto_select(candidates)
        rows.append(
            {
                "slot_id": slot_id,
                "narration_excerpt": slot.get("narration_excerpt"),
                "visual_archetype": slot.get("visual_archetype"),
                "motion_recipe": slot.get("motion_recipe"),
                "duration_s": slot.get("duration_s"),
                "on_screen_text": slot.get("on_screen_text"),
                "copy_deferred": slot.get("copy_deferred") is True,
                "candidates": candidates,
                "selected": selected,
                "selected_candidate_id": (selected or {}).get("id"),
                "auto_selected": selected is not None,
                "exceptions": _candidate_exceptions(selected),
            }
        )
    _mark_near_duplicates(rows)

    payload = {
        "schema_version": SCENE_BOARD_VERSION,
        "brief_hash": _bound_hash(brief_payload),
        "coverage_hash": _bound_hash(coverage_payload),
        "pack_hash": _bound_hash(pack_payload),
        "candidate_batch_hash": _bound_hash(batch_payload),
        "timing_basis": coverage_payload.get("timing_basis", "canonical"),
        "lane": pack_payload.get("lane"),
        "title": brief_payload.get("title"),
        "resources": {
            "source_kind": attestation_payload.get("source_kind"),
            "source_ref": attestation_payload.get("source_ref"),
            "asserted_by": attestation_payload.get("asserted_by"),
            "asserted_at": attestation_payload.get("asserted_at"),
            "claim_basis": attestation_payload.get("claim_basis"),
            "references": list(attestation_payload.get("references") or []),
        },
        "slot_count": len(rows),
        "exception_count": sum(1 for row in rows if row["exceptions"]),
        "slots": rows,
    }
    return stamp_artifact_hash(payload)


def _esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def _candidate_html(candidate: Mapping[str, Any], *, is_default: bool) -> str:
    flags = ", ".join(_esc(flag) for flag in candidate.get("qc_flags") or []) or "clean"
    checked = " checked" if is_default else ""
    slot_id = _esc(candidate.get("slot_id"))
    cid = _esc(candidate.get("id"))
    return (
        f'<label class="cand{" default" if is_default else ""}">'
        f'<input type="radio" name="{slot_id}" value="{cid}"{checked}>'
        f'<img src="{_esc(candidate.get("path"))}" alt="{cid}" loading="lazy">'
        f'<span class="meta">v{_esc(candidate.get("variant_index"))} &middot; {cid}'
        f'<br><span class="flags">{flags}</span></span></label>'
    )


def _slot_html(row: Mapping[str, Any]) -> str:
    exceptions = row.get("exceptions") or []
    banner = ""
    if exceptions:
        reasons = " &middot; ".join(_EXCEPTION_REASONS.get(name, name) for name in exceptions)
        banner = f'<p class="exception">Needs review: {reasons}</p>'
    copy_note = (
        '<p class="deferred">On-screen copy deferred to the operator.</p>'
        if row.get("copy_deferred")
        else ""
    )
    cards = "".join(
        _candidate_html(candidate, is_default=candidate.get("id") == row.get("selected_candidate_id"))
        for candidate in row.get("candidates") or []
    ) or '<p class="empty">No candidates returned for this slot.</p>'
    video_state = "ready" if row.get("selected_candidate_id") else "blocked"
    return f"""<section class="slot{' flagged' if exceptions else ''}" id="slot-{_esc(row['slot_id'])}">
  <header><h3>{_esc(row['slot_id'])}</h3>
  <span class="tags">{_esc(row.get('visual_archetype'))} &middot; {_esc(row.get('motion_recipe'))} &middot; {_esc(row.get('duration_s'))}s</span></header>
  {banner}
  <blockquote>{_esc(row.get('narration_excerpt'))}</blockquote>
  {copy_note}
  <div class="cands">{cards}</div>
  <div class="tier3" data-state="{video_state}">Tier 3 &middot; video generation
    <span class="disabled-pill">disabled &mdash; no provider bound</span></div>
</section>"""


_STYLE = """
:root{color-scheme:light dark}
body{font:15px/1.5 system-ui,sans-serif;margin:0;padding:24px;background:#fbfbfd;color:#16161a}
h1{margin:0 0 4px;font-size:22px}
.sub{color:#666;margin:0 0 20px}
.resources{background:#fff;border:1px solid #e3e3ea;border-radius:10px;padding:14px 16px;margin-bottom:24px}
.resources dt{font-weight:600;font-size:12px;text-transform:uppercase;color:#777;margin-top:8px}
.resources dd{margin:2px 0 0}
.banner{background:#fff4e5;border:1px solid #f0c894;border-radius:8px;padding:10px 14px;margin-bottom:20px}
.slot{background:#fff;border:1px solid #e3e3ea;border-radius:10px;padding:14px 16px;margin-bottom:16px}
.slot.flagged{border-color:#e0913c;box-shadow:0 0 0 2px #fbe6cd}
.slot header{display:flex;justify-content:space-between;align-items:baseline;gap:12px;flex-wrap:wrap}
.slot h3{margin:0;font-size:15px;font-family:ui-monospace,monospace}
.tags{color:#777;font-size:12px}
.exception{color:#a4560c;font-weight:600;margin:8px 0 0}
.deferred{color:#5a4b8a;font-size:13px;margin:6px 0 0}
blockquote{margin:10px 0;padding-left:12px;border-left:3px solid #dcdce4;color:#444}
.cands{display:flex;gap:12px;flex-wrap:wrap;margin-top:10px}
.cand{border:2px solid #e3e3ea;border-radius:8px;padding:6px;cursor:pointer;max-width:220px}
.cand.default{border-color:#3b7de0}
.cand img{display:block;width:200px;height:auto;border-radius:4px;background:#eee}
.meta{display:block;font-size:11px;color:#666;margin-top:4px;font-family:ui-monospace,monospace}
.flags{color:#a4560c}
.tier3{margin-top:12px;padding:8px 10px;border:1px dashed #c9c9d4;border-radius:8px;color:#777;font-size:13px}
.disabled-pill{background:#ececf2;border-radius:999px;padding:2px 8px;margin-left:8px;font-size:11px}
.empty{color:#a00}
button{font:inherit;padding:8px 14px;border-radius:8px;border:1px solid #3b7de0;background:#3b7de0;color:#fff;cursor:pointer}
pre{background:#111;color:#d8d8e0;padding:12px;border-radius:8px;overflow:auto;max-height:260px}
@media(prefers-color-scheme:dark){body{background:#131317;color:#e8e8ef}
.resources,.slot{background:#1c1c22;border-color:#2e2e38}
blockquote{color:#bdbdc8;border-color:#3a3a46}pre{background:#000}}
"""

_SCRIPT = """
function collect(){
  const out=[];
  document.querySelectorAll('section.slot').forEach(function(s){
    const picked=s.querySelector('input[type=radio]:checked');
    out.push({slot_id:s.id.replace(/^slot-/,''),candidate_id:picked?picked.value:null});
  });
  const text=JSON.stringify({schema_version:'scene_board_selection.v1',selections:out},null,2);
  document.getElementById('payload').textContent=text;
  if(navigator.clipboard){navigator.clipboard.writeText(text);}
}
"""


def render_board_html(board: Mapping[str, Any]) -> str:
    """Static, offline, theme-aware board page."""

    rows = list(board.get("slots") or [])
    flagged = [row for row in rows if row.get("exceptions")]
    clean = [row for row in rows if not row.get("exceptions")]
    resources = board.get("resources") or {}
    refs = "".join(
        f"<dd>{_esc(ref.get('kind'))}: {_esc(ref.get('ref'))}</dd>"
        for ref in resources.get("references") or []
    ) or "<dd>none attached</dd>"

    banner = (
        f'<p class="banner"><strong>{len(flagged)} of {len(rows)} slots need review.</strong> '
        "Every other slot already has an auto-selected default; you only have to touch the "
        "flagged ones.</p>"
    )
    timing = board.get("timing_basis")
    if timing == "estimated":
        banner += (
            '<p class="banner">Timing is <strong>estimated</strong> from word count. '
            "Valid for layout and slot counting; the render clock still comes from audio.</p>"
        )

    body = "".join(_slot_html(row) for row in flagged + clean)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Scene Board &middot; {_esc(board.get('title'))}</title>
<style>{_STYLE}</style></head>
<body>
<h1>{_esc(board.get('title'))}</h1>
<p class="sub">{_esc(board.get('lane'))} &middot; {_esc(board.get('slot_count'))} slots &middot;
coverage <code>{_esc(str(board.get('coverage_hash'))[:12])}</code></p>
{banner}
<dl class="resources"><dt>Tier 1 &middot; attested source</dt>
<dd>{_esc(resources.get('source_kind'))}: {_esc(resources.get('source_ref'))}</dd>
<dt>Asserted by</dt><dd>{_esc(resources.get('asserted_by'))} at {_esc(resources.get('asserted_at'))}</dd>
<dt>Claim basis</dt><dd>{_esc(resources.get('claim_basis'))}</dd>
<dt>References</dt>{refs}</dl>
<h2>Tier 2 &middot; image candidates</h2>
{body}
<p><button onclick="collect()">Copy selection JSON</button></p>
<pre id="payload">Press the button to emit the selection payload.</pre>
<script>{_SCRIPT}</script>
</body></html>"""


def render_scene_board(
    *,
    coverage: Mapping[str, Any] | str | Path,
    pack: Mapping[str, Any] | str | Path,
    batch: Mapping[str, Any] | str | Path,
    brief: Mapping[str, Any] | str | Path,
    attestation: Mapping[str, Any] | str | Path,
    output_dir: str | Path,
) -> dict[str, Any]:
    """Write ``board/board.json`` and ``board/index.html``."""

    board = build_board(
        coverage=coverage, pack=pack, batch=batch, brief=brief, attestation=attestation
    )
    board_dir = Path(output_dir) / "board"
    json_path = write_artifact(board_dir / "board.json", board)
    html_path = board_dir / "index.html"
    html_path.write_text(render_board_html(board), encoding="utf-8")
    return {
        "board_path": str(html_path),
        "board_json_path": str(json_path),
        "board_hash": board["artifact_hash"],
        "slot_count": board["slot_count"],
        "exception_count": board["exception_count"],
        "auto_selected": sum(1 for row in board["slots"] if row.get("auto_selected")),
    }
