"""Index every generated plate across every source into one queryable library.

Built 2026-08-29 after a session in which assets were repeatedly missed
because of WHERE they sat rather than WHAT they were:

  - 195 approved pilot plates skipped for living in a folder named
    `quarantine/` while every manifest inside read
    `operator_approved_for_composition`
  - 86 teacher-stamped visuals unresolvable because they are keyed by
    `image_id` and stored under `extracted_path`
  - a shot table authored from `objects/*.png` filenames while the
    `semantic` field describing each plate sat unread in the manifest
    beside it

The library records, for every plate: its id, its real path, its SEMANTIC
(what it depicts — the thing you actually select on), its style register,
its approval state as the MANIFEST states it, and its source.

**Status comes from the manifest, never from the path** (ruling E10).

Usage:
    python build_plate_library.py                 # rebuild the index
    python build_plate_library.py "memory stack"  # search it
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
MAIN = Path(r"C:\Users\Snipe\Downloads\Outreach Program")
CODEX = Path(r"C:\Users\Snipe\.codex\worktrees\f10b\Outreach Program")
OUT = REPO / "content/video_engine/sources/PLATE-LIBRARY.json"

APPROVED = ("approved", "operator_approved", "operator_verified",
            "operator_approved_for_composition",
            "operator_approved_for_trace_cut")


def load(p: Path) -> dict:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:                                       # noqa: BLE001
        return {}


def state_of(manifests: list[dict]) -> tuple[str, bool]:
    """The approval state as the MANIFESTS record it, and render-eligibility."""
    states, render = set(), False
    for d in manifests:
        for k in ("review_state", "status", "operator_decision"):
            if isinstance(d.get(k), str):
                states.add(d[k])
        if d.get("render_eligible") is True:
            render = True
        if d.get("operator_approved"):
            states.add("operator_approved")
    ok = any(s in APPROVED or s.startswith("operator_approved") for s in states)
    return ("approved" if ok else (", ".join(sorted(states)) or "unstated")), render


def scan_claim_waves(root: Path, source: str, register: str) -> list[dict]:
    """Episode plate waves: semantics live in <wave>/*.manifest.json."""
    out = []
    for wave in sorted(root.glob("*plate*")):
        if not wave.is_dir():
            continue
        # a claim folder may BORROW another lane's register (ruling C9);
        # its approvals.json declares which, so the path never decides.
        reg = register
        ap = load(wave / "approvals.json")
        if "register" in ap:
            reg = ap["register"]
        mans = [load(f) for f in wave.glob("*.json")]
        sem = {}
        for d in mans:
            for a in d.get("assets", []):
                if a.get("asset_id"):
                    sem[a["asset_id"]] = a.get("semantic", "")
        approved = set()
        for d in mans:
            approved |= set(d.get("operator_approved") or [])
        st, render = state_of(mans)
        for png in sorted((wave / "objects").glob("*.png")):
            out.append({
                "id": png.stem, "path": str(png), "semantic": sem.get(png.stem, ""),
                "register": reg, "source": f"{source}/{wave.name}",
                "state": "approved" if (png.stem in approved or st == "approved")
                         else st,
                "render_eligible": render or png.stem in approved,
            })
    return out


def scan_pilot(root: Path) -> list[dict]:
    """The pilot library. `quarantine/` is MISNAMED — read the manifests."""
    out = []
    for sub, reg in (("hero", "cut-paper-ukiyo"),
                     ("components", "keyed-overlay"),
                     ("quarantine", "sentence-native")):
        d0 = root / sub
        if not d0.is_dir():
            continue
        for wave in sorted([d0] if sub == "hero" else
                           [x for x in d0.iterdir() if x.is_dir()]):
            mans = [load(f) for f in wave.glob("*.json")]
            st, render = state_of(mans)
            if sub == "hero":
                st, render = "approved", True   # assets/hero is the shipped set
            for png in sorted(wave.glob("*.png")):
                if png.stem.endswith(("--background", "--midground",
                                      "--foreground", "--contact-shadow",
                                      "--negative-space")):
                    continue          # depth layers, not standalone plates
                out.append({
                    "id": png.stem, "path": str(png), "semantic": "",
                    "register": reg,
                    "source": f"pilot/current-bubble-mechanism/{sub}/{wave.name}",
                    "state": st, "render_eligible": render,
                })
    return out


def main() -> int:
    if len(sys.argv) > 1:
        lib = json.loads(OUT.read_text(encoding="utf-8"))
        q = " ".join(sys.argv[1:]).lower()
        hits = [p for p in lib["plates"]
                if q in p["id"].lower() or q in p["semantic"].lower()]
        print(f"{len(hits)} of {len(lib['plates'])} plates match {q!r}\n")
        for p in hits[:40]:
            print(f"  {p['id'][:44]:<46}{p['register']:<17}{p['semantic'][:56]}")
        return 0

    plates = []
    plates += scan_claim_waves(
        REPO / "content/video_engine/projects/systems-and-blowups/review/claims",
        "steel-and-paper", "woodblock-vox-newsprint")
    pilot = CODEX / ("content/video_engine/projects/systems-and-blowups/"
                     "pilots/current-bubble-mechanism/assets")
    if pilot.is_dir():
        plates += scan_pilot(pilot)

    seen, uniq = set(), []
    for p in plates:
        if p["id"] not in seen:
            seen.add(p["id"])
            uniq.append(p)

    from collections import Counter
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "schema_version": "plate_library.v1",
        "built": "2026-08-29",
        "note": "Status comes from the MANIFEST, never the path (ruling E10). "
                "The pilot's quarantine/ directory is misnamed - every "
                "manifest inside reads operator_approved.",
        "count": len(uniq), "plates": uniq,
    }, indent=1), encoding="utf-8")

    print(f"PLATE LIBRARY — {len(uniq)} plates indexed -> {OUT.name}\n")
    for k, v in Counter(p["register"] for p in uniq).most_common():
        print(f"  {v:4d}  {k}")
    print()
    for k, v in Counter(p["state"] for p in uniq).most_common():
        print(f"  {v:4d}  {k}")
    print(f"\n  {sum(1 for p in uniq if p['semantic'])} carry a written semantic")
    print(f"  {sum(1 for p in uniq if p['render_eligible'])} render-eligible")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
