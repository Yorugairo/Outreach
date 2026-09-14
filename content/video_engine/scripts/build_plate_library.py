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


# ---- P58 T2 / ruling E98 s6 - THE DEPTH LAYERS A PLATE DECLARES --------------------------------
#
# A plate ships FLAT or it ships in PLANES. Doc 24 ("2.5D depth planes",
# `24-COMPOSITION-AND-SCALE-SPEC.md:156`) has named the planes, their file suffixes and their
# parallax factors since the ep1 era, and doc 23 s11 recorded the only missing piece: "worlds ship
# as one flat image, so parallax has nothing to separate". P50 T7/T15 already put a sidecar beside
# the plate - `<plate>.layers.json`, "A sidecar, not a new asset id ... it is part of THIS plate,
# and it travels with it". This adds ONE key to that same sidecar, never a second file:
#
#   {"foreground": {...}, "embed": {...},
#    "layers": [{"path": "<png beside the plate>", "role": "background|board|mid|subject|occluder",
#                "depth": <parallax factor k>, "alpha": true,
#                "generator": "gpt-image-2.5|gpt-image-2.0|depth-split|depth-split-sam|flow"}]}
#
# declared BACK TO FRONT, `depth` ASCENDING toward the viewer.
#
# `depth` IS DOC 24'S PARALLAX FACTOR k (1.0 at the wall, 1.40 at the near cutout), not a 0..1 -
# the PRP's "<0..1>" was a placeholder, and a 0..1 would need a second table to become the number
# the camera multiplies by (T3 takes `k` straight: offset = (at - look) * k).
#
# THE SUBJECT PLANE'S DEFAULT IS DERIVED. Doc 24's table has four rows - `-far` 1.0, `-board` 1.05,
# `-mid` 1.15, `-near` 1.40 - and no row for the cast: "The cast composites between `mid` and
# `near`". So `subject` takes the MIDPOINT of those two factors, 1.275, and this is the only number
# here the doc does not state; every other one is quoted from it.
#
# `generator` IS E98 s6 MADE AUDITABLE - the operator, 2026-09-14: a layer is GENERATED, never cut
# out of a stacked generation; the depth split (`comfy_depth_split.py`) is the FALLBACK for an
# existing flat plate. Both origins are legal, so every layer records which one it is, and an
# unknown origin is refused by name rather than indexed as an unattributable plane.
LAYERS_SUFFIX = ".layers.json"
LAYER_PLANES: dict[str, tuple[str, float]] = {   # role -> (doc 24 `depth_layer`, parallax factor)
    "background": ("building_or_environment", 1.0),
    "board": ("evidence_safe_region", 1.05),
    "mid": ("actor_or_machine", 1.15),
    "subject": ("cast_between_mid_and_near", round((1.15 + 1.40) / 2, 4)),   # DERIVED, see above
    "occluder": ("foreground_cutout", 1.40),
}
LAYER_DEPTH_DERIVED = ("subject",)               # the roles whose default doc 24 does not state
LAYER_GENERATORS = ("gpt-image-2.5", "gpt-image-2.0", "depth-split", "depth-split-sam", "flow")
FLAT_BACK_CATALOGUE = "pre-E98 back catalogue"


def png_has_alpha(p: Path) -> bool:
    """Does this PNG carry a transparency channel? (IHDR colour type 4/6, or a palette + tRNS.)"""
    try:
        with p.open("rb") as fh:
            head = fh.read(64)
    except OSError:
        return False
    if head[:8] != b"\x89PNG\r\n\x1a\n" or len(head) < 26:
        return False
    colour = head[25]
    if colour in (4, 6):
        return True
    return colour == 3 and b"tRNS" in p.read_bytes()


def read_sidecar(plate: Path) -> dict:
    """The plate's sidecar, or {} - a plate is not required to have one."""
    try:
        data = json.loads(Path(plate).with_suffix(LAYERS_SUFFIX).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def flat_reason(plate: Path, sidecar: dict | None = None) -> str:
    """Why this plate ships flat. The author may say; otherwise it is the back catalogue."""
    data = read_sidecar(plate) if sidecar is None else sidecar
    own = data.get("flat_reason")
    return own.strip() if isinstance(own, str) and own.strip() else FLAT_BACK_CATALOGUE


def _layer_record(plate: Path, entry, i: int, where: str) -> dict:
    """One declared plane, every default filled - or the refusal that names what to fix."""
    tag = f"{where}: layers[{i}]"
    if not isinstance(entry, dict):
        raise ValueError(f"{tag} is {type(entry).__name__}, not an object - a plane is "
                         "{path, role, depth, alpha, generator}")
    role = entry.get("role")
    if role not in LAYER_PLANES:
        raise ValueError(f"{tag} has role {role!r}, which is not a depth plane - name one of "
                         f"{', '.join(LAYER_PLANES)} (doc 24, '2.5D depth planes')")
    tag = f"{tag} ({role})"
    rel = entry.get("path")
    if not isinstance(rel, str) or not rel.strip():
        raise ValueError(f"{tag} needs 'path', the layer PNG beside the plate")
    f = (Path(plate).parent / rel.strip()).resolve()
    if not f.is_file():
        raise ValueError(f"{tag} points at {rel!r}, which is not on disk - generate the plane or "
                         f"fix the path (it resolves beside the plate, at {f})")
    depth = entry.get("depth", LAYER_PLANES[role][1])
    if isinstance(depth, bool) or not isinstance(depth, (int, float)) or not 0 < float(depth) <= 4:
        raise ValueError(f"{tag} has depth {depth!r} - depth is doc 24's parallax FACTOR k in "
                         f"(0, 4], not a 0..1; omit it for this role's default "
                         f"{LAYER_PLANES[role][1]}")
    alpha = entry.get("alpha", role != "background")     # doc 24: -far is opaque, the rest are not
    if not isinstance(alpha, bool):
        raise ValueError(f"{tag} has alpha {alpha!r} - alpha is true or false (does the PNG carry "
                         "a transparency channel)")
    if alpha and not png_has_alpha(f):
        raise ValueError(f"{tag} declares alpha: true but {f.name} has no alpha channel - "
                         "re-export it as RGBA (doc 24: -far is opaque, every other plane is "
                         "transparent), or declare alpha: false")
    gen = entry.get("generator")
    if gen not in LAYER_GENERATORS:
        raise ValueError(f"{tag} has generator {gen!r} - every plane records its origin "
                         f"(ruling E98 s6: generated, or split out of a flat plate): one of "
                         f"{', '.join(LAYER_GENERATORS)}")
    return {"path": rel.strip(), "file": str(f), "role": role, "plane": LAYER_PLANES[role][0],
            "depth": round(float(depth), 4), "alpha": alpha, "generator": gen}


def _refuse_layer_set(layers: list[dict], where: str) -> None:
    """The three ways a set of planes is wrong even when every plane is right."""
    roles = [l["role"] for l in layers]
    dup = [r for r in roles if roles.count(r) > 1]
    if dup:
        raise ValueError(f"{where}: role {sorted(set(dup))[0]!r} is declared twice - one plane per "
                         "role, and a second cutout at the same depth belongs in the same PNG")
    if "background" not in roles:
        raise ValueError(f"{where}: this layered plate has no 'background' plane - the opaque -far "
                         "wall every other plane parallaxes against (doc 24); declare it, or drop "
                         "'layers' and let the plate read flat")
    depths = [l["depth"] for l in layers]
    if any(b <= a for a, b in zip(depths, depths[1:])):
        raise ValueError(f"{where}: layers are not ordered back to front - depth must ASCEND "
                         f"toward the viewer, got {depths}; reorder the list (background first, "
                         "occluder last)")


def plate_depth_layers(plate: Path, sidecar: dict | None = None) -> list[dict] | None:
    """The DEPTH planes a plate declares, back to front, or None when the plate ships flat.

    Every way a layered plate goes wrong silently is refused BY NAME with the fix in the message -
    a plane that is not on disk, planes out of order, a duplicated role, no background, a declared
    alpha the PNG does not have, an undeclared role, an unrecorded origin. Each of those would
    otherwise resolve to a frame nobody could explain: a plate that simply never separated.
    """
    plate = Path(plate)
    data = read_sidecar(plate) if sidecar is None else sidecar
    raw = data.get("layers")
    if raw is None:
        return None
    where = plate.name
    if not isinstance(raw, list) or not raw:
        raise ValueError(f"{where}: 'layers' must be a non-empty list of planes declared back to "
                         "front; a plate with no planes carries no 'layers' key at all")
    layers = [_layer_record(plate, e, i, where) for i, e in enumerate(raw)]
    _refuse_layer_set(layers, where)
    return layers


def index_layers(plates: list[dict]) -> tuple[list[dict], list[str]]:
    """Carry each plate's planes onto its record, or mark it flat, and drop any PNG that is a
    LAYER of another plate (P50 T15 - a layer can never be a plate of its own). Returns the
    records that survive and every refusal, which the caller prints and exits non-zero on: a
    sidecar that does not hold is never quietly re-read as a flat plate.
    """
    refusals: list[str] = []
    layer_files: set[str] = set()
    for p in plates:
        plate = Path(p["path"])
        try:
            layers = plate_depth_layers(plate)
        except ValueError as exc:
            refusals.append(str(exc))
            p["flat"], p["flat_reason"] = True, f"layers refused - {exc}"
            continue
        if layers:
            p["layers"] = layers
            layer_files |= {l["file"].lower() for l in layers}
        else:
            p["flat"], p["flat_reason"] = True, flat_reason(plate)
    kept = [p for p in plates
            if str(Path(p["path"]).resolve()).lower() not in layer_files]
    return kept, refusals


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


def scan_project_plates(repo: Path) -> list[dict]:
    """A project registers a plate of its own: `<project>/assets/plates/*.png`.

    The claim waves are where a plate is BORN (a work order, a manifest, an approvals file); a
    plate that arrives any other way - the P58 probe's reference world, generated to be split -
    still needs one home the index scans. `plates.json` beside the PNGs carries each plate's
    record, so nothing here is inferred from a path (ruling E10), and `state` stays whatever the
    manifest said: an agent's self-judgement is never an approval.
    """
    out = []
    folders = sorted(set(list(repo.glob("content/video_engine/projects/*/assets/plates"))
                         + list(repo.glob("content/video_engine/projects/*/*/assets/plates"))))
    for folder in folders:
        meta = (load(folder / "plates.json") or {}).get("plates") or {}
        # an entry may NAME a plate that lives elsewhere in the project (`path`, relative to the
        # project root); otherwise a plate is the PNG sitting beside plates.json under its stem
        named: dict[str, Path] = {}
        for pid, e in meta.items():
            rel = e.get("path")
            if isinstance(rel, str) and rel.strip():
                named[pid] = (folder.parents[1] / rel.strip()).resolve()
        for png in sorted(folder.glob("*.png")):
            named.setdefault(png.stem, png)
        for pid, png in sorted(named.items()):
            if not png.is_file():
                print(f"  MISSING  {pid}: {folder.name}/plates.json names {png}, "
                      "which is not on disk - fix the path or drop the entry")
                continue
            e = dict(meta.get(pid) or {})
            out.append({
                "id": pid, "path": str(png),
                "semantic": e.get("semantic", ""),
                "register": e.get("register", ""),
                "channel": e.get("channel", "money-physics"),
                "source": e.get("source", f"{folder.parents[1].name}/assets/plates"),
                "state": e.get("state", "unstated"),
                "render_eligible": bool(e.get("render_eligible")),
                **({"generator": e["generator"]} if e.get("generator") else {}),
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
    plates += scan_project_plates(REPO)

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

    # every record now reads LAYERED or FLAT, and a layer PNG is never a plate (P58 T2)
    uniq, refusals = index_layers(uniq)

    from collections import Counter
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "schema_version": "plate_library.v2",
        "built": "2026-08-29",
        "note": "Status comes from the MANIFEST, never the path (ruling E10). "
                "The pilot's quarantine/ directory is misnamed - every "
                "manifest inside reads operator_approved. v2 (P58 T2): every "
                "plate reads `layers` - doc 24's depth planes, back to front, "
                "declared in <plate>.layers.json - or `flat` + `flat_reason`.",
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
    print(f"  {sum(1 for p in uniq if p.get('layers'))} declare depth layers, "
          f"{sum(1 for p in uniq if p.get('flat'))} flat")
    for msg in refusals:
        print(f"  REFUSED  {msg}")
    return 1 if refusals else 0


if __name__ == "__main__":
    raise SystemExit(main())
