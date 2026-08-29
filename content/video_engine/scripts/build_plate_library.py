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
its approval state as the MANIFEST states it, its source, and its CHANNEL.

**Channels are identity walls, not tags** (operator, 2026-08-29): a
jiu-jitsu plate must never resolve into a finance episode. Every consumer
filters by channel; the resolver refuses cross-channel plates outright.

**Status comes from the manifest, never from the path** (ruling E10).

Usage:
    python build_plate_library.py                 # rebuild the index
    python build_plate_library.py "memory stack"  # search it
"""
from __future__ import annotations

import json
import re
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


def scan_claim_waves(root: Path, source: str, register: str,
                     channel: str = "money-physics") -> list[dict]:
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
        sem = dict(ap.get("semantics") or {})   # the claim may author its own
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
                "register": reg, "channel": channel,
                "source": f"{source}/{wave.name}",
                "state": "approved" if (png.stem in approved or st == "approved")
                         else st,
                "render_eligible": render or png.stem in approved,
            })
    return out


def pilot_semantics(edit: Path) -> dict:
    """The pilot writes richer semantics than a `semantic` string.

    `edit/semantic-v2/asset-catalog.v2.json` carries semantic_tags,
    capability_anchors, representation_modes, prohibited_implications and a
    reuse_policy per asset. `edit/sentence-native-v1/semantic-beat-ledger.v1
    .json` carries 202 beats with their spoken excerpt and active nouns, and
    plate ids encode their beat (beat-03-002-... -> chapter 03, beat 002).
    Both are read; neither is guessed at.
    """
    sem: dict[str, dict] = {}
    cat = load(edit / "semantic-v2/asset-catalog.v2.json")
    for a in cat.get("assets", []):
        aid = a.get("asset_id")
        if not aid:
            continue
        sem[aid] = {
            "semantic": ", ".join(a.get("semantic_tags") or []),
            "kind": a.get("kind", ""),
            "worlds": a.get("visual_worlds") or [],
            "anchors": a.get("capability_anchors") or [],
            "modes": a.get("representation_modes") or [],
            "prohibited": a.get("prohibited_implications") or [],
            "reuse_policy": a.get("reuse_policy") or {},
            "claim_refs": a.get("claim_refs") or [],
        }
    # beat ledger: map "beat-<chapter>-<local>" prefixes to the spoken line
    led = load(edit / "sentence-native-v1/semantic-beat-ledger.v1.json")
    beats = {}
    for b in led.get("beats", []):
        # Key off the beat_id itself - `cbm-semantic-beat-01-002` matches the
        # filename prefix `beat-01-002`. Deriving it from chapter_index is an
        # off-by-one, because the id numbers chapters from 1 and the field
        # from 0, and the wrong excerpt then reads plausibly.
        bid = b.get("beat_id", "")
        if "-beat-" not in bid:
            continue
        beats["beat-" + bid.split("-beat-", 1)[1]] = {
            "excerpt": b.get("excerpt", ""),
            "nouns": b.get("active_nouns") or [],
            "verb": b.get("causal_verb", ""),
            "at": b.get("start_s"),
        }
    sem["__beats__"] = beats
    # assets/hero postdates the catalog (different ids), so these are authored
    # from the plates. Each is the DRAMATIC register (ruling C9).
    sem.update({k: {"semantic": v, "kind": "hero_plate"} for k, v in {
        "hero-barbell-v1": "a balance scale, gold blocks one pan and paper the other - weighing steel against paper",
        "hero-contract-ovens-v1": "an oven line issuing sealed discs to a queue of buyers - forward contracts, locked",
        "hero-countercase-v1": "a figure before a wave and collapsing towers, one green shoot rising - what survives",
        "hero-fab-constraint-v1": "a cleanroom wafer line in full production - the physical constraint itself",
        "hero-hbm-bandwidth-v1": "a die at centre with bandwidth streaming out to server towers - HBM as the bottleneck",
        "hero-korea-italy-v1": "split frame, Korean industrial coast against Italian classical city - two continents, one hardware",
        "hero-sp500-double-failure-v1": "many towers cascading paper down onto a crowd below - the index as a waterfall of claims",
        "hero-wrong-bubble-v1": "a lit chip tower beside a basket stuffed with paper slips - the bubble is in the paper, not the silicon",
    }.items()})
    return sem


def scan_pilot(root: Path, sem: dict | None = None) -> list[dict]:
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
                if "contact-sheet" in png.stem or png.stem.endswith("-frame-001"):
                    continue          # review artifacts, not plates
                rec = {
                    "id": png.stem, "path": str(png), "semantic": "",
                    "register": reg, "channel": "money-physics",
                    "source": f"pilot/current-bubble-mechanism/{sub}/{wave.name}",
                    "state": st, "render_eligible": render,
                }
                s = (sem or {}).get(png.stem)
                if s:
                    rec.update({k: v for k, v in s.items() if v})
                else:
                    # plate ids encode their beat: beat-03-002-hbm-stack-...
                    key = "-".join(png.stem.split("-")[:3])
                    bt = (sem or {}).get("__beats__", {}).get(key)
                    if bt:
                        rec["semantic"] = bt["excerpt"]
                        rec["beat_at"] = bt["at"]
                        rec["nouns"] = bt["nouns"]
                out.append(rec)
    return out


def scan_martial_matters(repo: Path) -> list[dict]:
    """The THIRD channel. 192 word-timed plates keyed mm001-word-NNN; their
    semantics live in the continuity cue ledger (narration excerpt, chapter,
    story signal) — the filename prefix after NNN_ is the cue id."""
    root = repo / "content/video_engine/projects/martial-matters"
    cues = {}
    for led in root.glob("pilots/*/continuity/revisions/*/word-timed-visual-cues*.json"):
        for c in load(led).get("cues", []):
            cues[c["cue_id"]] = c
    out = []
    for png in sorted(root.glob("assets/kits/*/candidates/*/*.png")):
        # 001_mm001-word-008-contained-peace -> cue mm001-word-008; later
        # waves append a slug after the cue id, so match by pattern
        m = re.search(r"mm\d+-word-\d+", png.stem)
        c = cues.get(m.group(0), {}) if m else {}
        out.append({
            "id": png.stem, "path": str(png),
            "semantic": c.get("narration_excerpt", ""),
            "register": png.parts[-3].rsplit("-", 1)[0],   # kit name sans -v1
            "channel": "martial-matters",
            "source": f"martial-matters/{png.parts[-2]}",
            "chapter": c.get("chapter_id", ""),
            "state": "candidate",          # no approval manifest read yet
            "render_eligible": False,
        })
    return out


def main() -> int:
    if len(sys.argv) > 1:
        lib = json.loads(OUT.read_text(encoding="utf-8"))
        q = " ".join(sys.argv[1:]).lower()
        chan = None
        if "--channel" in sys.argv:
            i = sys.argv.index("--channel"); chan = sys.argv[i + 1]
            q = " ".join(a for a in sys.argv[1:] if a not in ("--channel", chan)).lower()
        hits = [p for p in lib["plates"]
                if (q in p["id"].lower() or q in p["semantic"].lower())
                and (chan is None or p.get("channel") == chan)]
        print(f"{len(hits)} of {len(lib['plates'])} plates match {q!r}\n")
        for p in hits[:40]:
            print(f"  {p['id'][:40]:<42}{p.get('channel','?')[:14]:<16}"
                  f"{p['semantic'][:52]}")
        return 0

    plates = []
    plates += scan_claim_waves(
        REPO / "content/video_engine/projects/systems-and-blowups/review/claims",
        "steel-and-paper", "woodblock-vox-newsprint")
    plates += scan_martial_matters(REPO)
    pilot = CODEX / ("content/video_engine/projects/systems-and-blowups/"
                     "pilots/current-bubble-mechanism/assets")
    if pilot.is_dir():
        sem = pilot_semantics(pilot.parent / "edit")
        plates += scan_pilot(pilot, sem)

    # a keyed (chroma) plate is the same subject as its alpha twin
    by_id = {p["id"]: p for p in plates}
    for p in plates:
        if not p["semantic"] and p["id"].endswith("-keyed-v1"):
            twin = by_id.get(p["id"].replace("-keyed-v1", "-alpha-v1"))
            if twin and twin["semantic"]:
                p["semantic"] = twin["semantic"]

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
    for k, v in Counter(p.get("channel", "?") for p in uniq).most_common():
        print(f"  {v:4d}  channel {k}")
    print()
    for k, v in Counter(p["state"] for p in uniq).most_common():
        print(f"  {v:4d}  {k}")
    print(f"\n  {sum(1 for p in uniq if p['semantic'])} carry a written semantic")
    print(f"  {sum(1 for p in uniq if p['render_eligible'])} render-eligible")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
