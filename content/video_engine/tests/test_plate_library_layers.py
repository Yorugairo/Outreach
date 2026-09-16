"""A PLATE DECLARES ITS LAYERS, AND THE INDEX KNOWS (P58 T2; ruling E98 s6).

Doc 24 ("2.5D depth planes", `24-COMPOSITION-AND-SCALE-SPEC.md:156`) has named the four depth
planes, their file suffixes and their parallax factors since the ep1 era; doc 23 s11 recorded the
only missing piece - "worlds ship as one flat image, so parallax has nothing to separate". P50
T7/T15 put a sidecar beside the plate (`<plate>.layers.json`) and made it a NAMED SET the compiler
refuses by name. This slice adds ONE key to that same sidecar - `layers[]`, back to front, `depth`
ascending toward the viewer - carries it onto the plate library's record, and refuses every way a
layered plate can go wrong silently: a layer file that is not on disk, planes out of order, a
duplicated role, a layered plate with no background, a declared alpha the PNG does not have, an
undeclared role, and an unrecorded origin (E98 s6: a layer is GENERATED, never cut out of a stacked
generation - the depth split is the FALLBACK for an existing flat plate, so every layer says which
it is).

A plate with no `layers` reads `flat: true` with a `flat_reason`, written by the indexer and never
hand-maintained; and a layer PNG is never indexed as a plate of its own (P50 T15 - it is part of
THIS plate and it travels with it).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import build_plate_library as L  # noqa: E402

LIB = ROOT / "content/video_engine/sources/PLATE-LIBRARY.json"
PROJECTS = ROOT / "content/video_engine/projects/systems-and-blowups"
BANKER = (PROJECTS / "review/claims/finance-episodes-plates-wave-1/objects"
          / "world-banker-apartment-v2.png")
DOCK = PROJECTS / "tokyo-tea-break/assets/plates/world-tokyo-customs-dock-v1.png"
DOC24 = ROOT / "docs/content-video-engine/24-COMPOSITION-AND-SCALE-SPEC.md"
ROLES = ("background", "mid", "subject", "occluder")
BASE_FIELDS = {"id", "path", "semantic", "register", "channel", "source", "state",
               "render_eligible"}


# ---- fixtures: a plate, four planes beside it, one sidecar -------------------------------------

def _png(path: Path, alpha: bool = True) -> Path:
    Image.new("RGBA" if alpha else "RGB", (8, 8),
              (9, 9, 9, 255) if alpha else (9, 9, 9)).save(path)
    return path


def _planes(tmp_path: Path, roles=ROLES, alpha=True) -> list[dict]:
    out = []
    for r in roles:
        _png(tmp_path / f"world-fixture-v1-{r}.png", alpha=alpha)
        out.append({"path": f"world-fixture-v1-{r}.png", "role": r,
                    "alpha": True, "generator": "depth-split-sam"})
    return out


def _plate(tmp_path: Path, entries: list | None, **top) -> Path:
    plate = _png(tmp_path / "world-fixture-v1.png", alpha=False)
    side = tmp_path / "world-fixture-v1.layers.json"
    body = dict(top)
    if entries is not None:
        body["layers"] = entries
    side.write_text(json.dumps(body), encoding="utf-8")
    return plate


def _refusal(tmp_path: Path, entries: list) -> str:
    with pytest.raises(ValueError) as e:
        L.plate_depth_layers(_plate(tmp_path, entries))
    return str(e.value)


# ---- the table: doc 24's planes, and the one number doc 24 does not give ------------------------

def test_the_role_table_is_doc_24s_four_planes_and_their_parallax_factors():
    assert L.LAYER_PLANES["background"] == ("building_or_environment", 1.0)
    assert L.LAYER_PLANES["board"] == ("evidence_safe_region", 1.05)
    assert L.LAYER_PLANES["mid"] == ("actor_or_machine", 1.15)
    assert L.LAYER_PLANES["occluder"] == ("foreground_cutout", 1.40)


def test_the_subject_plane_is_DERIVED_because_doc_24s_table_has_no_row_for_it():
    table = DOC24.read_text(encoding="utf-8").split("## 2.5D depth planes", 1)[1][:1200]
    for suffix in ("`-far`", "`-board`", "`-mid`", "`-near`"):
        assert suffix in table
    assert "`-subject`" not in table                      # the cast has no row of its own
    assert "The cast composites between `mid` and `near`" in table
    plane, k = L.LAYER_PLANES["subject"]
    assert "subject" in L.LAYER_DEPTH_DERIVED             # the header says it is derived
    assert k == pytest.approx((1.15 + 1.40) / 2) == pytest.approx(1.275)


def test_depth_is_the_parallax_FACTOR_k_not_a_0_to_1(tmp_path):
    layers = L.plate_depth_layers(_plate(tmp_path, _planes(tmp_path)))
    assert [l["depth"] for l in layers] == [1.0, 1.15, 1.275, 1.40]


# ---- the happy path ----------------------------------------------------------------------------

def test_a_layered_plate_reads_back_to_front_with_every_default_filled(tmp_path):
    layers = L.plate_depth_layers(_plate(tmp_path, _planes(tmp_path)))
    assert [l["role"] for l in layers] == list(ROLES)
    assert [l["plane"] for l in layers] == ["building_or_environment", "actor_or_machine",
                                            L.LAYER_PLANES["subject"][0], "foreground_cutout"]
    assert all(l["generator"] == "depth-split-sam" and l["alpha"] is True for l in layers)
    assert all(Path(l["file"]).is_file() for l in layers)
    assert all(l["path"] == Path(l["file"]).name for l in layers)


def test_a_declared_depth_wins_over_the_default(tmp_path):
    entries = _planes(tmp_path)
    entries[2]["depth"] = 1.30
    assert [l["depth"] for l in L.plate_depth_layers(_plate(tmp_path, entries))] == \
        [1.0, 1.15, 1.30, 1.40]


def test_both_origins_are_legal_and_named_per_layer(tmp_path):
    assert L.LAYER_GENERATORS == ("gpt-image-2.5", "gpt-image-2.0", "depth-split",
                                  "depth-split-sam", "flow",
                                  "vace")   # + E99 s55 (P61 T14): the ambient lane's own backend, for an ALIVE plane
    entries = _planes(tmp_path)
    for e, g in zip(entries, ("gpt-image-2.5", "gpt-image-2.0", "depth-split", "flow")):
        e["generator"] = g
    assert [l["generator"] for l in L.plate_depth_layers(_plate(tmp_path, entries))] == \
        ["gpt-image-2.5", "gpt-image-2.0", "depth-split", "flow"]


# ---- the refusals, each BY NAME with the fix in the message -------------------------------------

def test_a_layer_file_not_on_disk_is_refused_by_name(tmp_path):
    entries = _planes(tmp_path)
    entries[3]["path"] = "world-fixture-v1-gone.png"
    msg = _refusal(tmp_path, entries)
    assert "layers[3] (occluder)" in msg and "world-fixture-v1-gone.png" in msg
    assert "not on disk" in msg and "beside the plate" in msg


def test_planes_out_of_order_are_refused_by_name(tmp_path):
    entries = _planes(tmp_path)
    entries[1]["depth"], entries[2]["depth"] = 1.30, 1.15
    msg = _refusal(tmp_path, entries)
    assert "not ordered back to front" in msg and "ASCEND toward the viewer" in msg
    assert "[1.0, 1.3, 1.15, 1.4]" in msg


def test_a_duplicated_role_is_refused_by_name(tmp_path):
    entries = _planes(tmp_path)
    entries[2]["role"] = "mid"
    msg = _refusal(tmp_path, entries)
    assert "'mid' is declared twice" in msg and "one plane per role" in msg


def test_a_layered_plate_with_no_background_is_refused_by_name(tmp_path):
    msg = _refusal(tmp_path, _planes(tmp_path)[1:])
    assert "no 'background' plane" in msg and "opaque" in msg


def test_a_declared_alpha_the_png_does_not_have_is_refused_by_name(tmp_path):
    entries = _planes(tmp_path)
    _png(tmp_path / "world-fixture-v1-subject.png", alpha=False)   # RGB, no alpha channel
    msg = _refusal(tmp_path, entries)
    assert "layers[2] (subject)" in msg and "declares alpha: true" in msg
    assert "no alpha channel" in msg and "RGBA" in msg


def test_an_opaque_background_may_declare_alpha_false(tmp_path):
    entries = _planes(tmp_path)
    entries[0]["alpha"] = False
    _png(tmp_path / "world-fixture-v1-background.png", alpha=False)
    layers = L.plate_depth_layers(_plate(tmp_path, entries))
    assert layers[0]["alpha"] is False and layers[0]["role"] == "background"


def test_an_unknown_role_is_refused_by_name(tmp_path):
    entries = _planes(tmp_path)
    entries[2]["role"] = "hero"
    msg = _refusal(tmp_path, entries)
    assert "role 'hero'" in msg and "not a depth plane" in msg
    assert "background, board, mid, subject, occluder" in msg


def test_an_unknown_or_missing_generator_is_refused_by_name(tmp_path):
    entries = _planes(tmp_path)
    entries[1]["generator"] = "midjourney"
    msg = _refusal(tmp_path, entries)
    assert "generator 'midjourney'" in msg and "E98" in msg
    assert "depth-split-sam" in msg
    bare = _planes(tmp_path)
    bare[1].pop("generator")
    assert "generator None" in _refusal(tmp_path, bare)


def test_a_layers_key_that_is_not_a_list_of_planes_is_refused_by_name(tmp_path):
    assert "non-empty list" in _refusal(tmp_path, [])
    with pytest.raises(ValueError) as e:
        L.plate_depth_layers(_plate(tmp_path, [{"role": "background",
                                                "generator": "depth-split"}]))
    assert "needs 'path'" in str(e.value)


# ---- flat, and the flag the indexer writes ------------------------------------------------------

def test_no_sidecar_at_all_is_flat_back_catalogue(tmp_path):
    plate = _png(tmp_path / "world-fixture-v1.png", alpha=False)
    assert L.plate_depth_layers(plate) is None
    assert L.flat_reason(plate) == L.FLAT_BACK_CATALOGUE == "pre-E98 back catalogue"


def test_a_sidecar_with_no_layers_key_is_flat_and_may_state_its_own_reason(tmp_path):
    plate = _plate(tmp_path, None, foreground={"lamp": "world-fixture-v1-occluder.png"})
    assert L.plate_depth_layers(plate) is None
    assert L.flat_reason(plate) == L.FLAT_BACK_CATALOGUE
    authored = _plate(tmp_path, None, flat_reason="a flat sky card, nothing to separate")
    assert L.flat_reason(authored) == "a flat sky card, nothing to separate"


def test_the_indexer_writes_flat_or_layers_on_every_record_and_never_both(tmp_path):
    layered = _plate(tmp_path, _planes(tmp_path))
    flat = _png(tmp_path / "world-flat-v1.png", alpha=False)
    recs, refusals = L.index_layers([{"id": p.stem, "path": str(p)} for p in (layered, flat)])
    assert refusals == []
    assert len(recs[0]["layers"]) == 4 and "flat" not in recs[0]
    assert recs[1]["flat"] is True and recs[1]["flat_reason"] == L.FLAT_BACK_CATALOGUE


def test_a_refused_sidecar_is_reported_and_never_silently_flat(tmp_path):
    entries = _planes(tmp_path)
    entries[3]["path"] = "gone.png"
    plate = _plate(tmp_path, entries)
    recs, refusals = L.index_layers([{"id": plate.stem, "path": str(plate)}])
    assert len(refusals) == 1 and "not on disk" in refusals[0]
    assert recs[0]["flat"] is True and recs[0]["flat_reason"].startswith("layers refused - ")
    assert "layers" not in recs[0]


# ---- P50 T15: a layer is part of THIS plate, never a plate of its own ---------------------------

def test_a_layer_png_is_not_indexed_as_a_plate_of_its_own(tmp_path):
    plate = _plate(tmp_path, _planes(tmp_path))
    scanned = [{"id": plate.stem, "path": str(plate)}] + [
        {"id": f"world-fixture-v1-{r}", "path": str(tmp_path / f"world-fixture-v1-{r}.png")}
        for r in ROLES]
    recs, refusals = L.index_layers(scanned)
    assert refusals == [] and [r["id"] for r in recs] == ["world-fixture-v1"]


# ---- the built index ----------------------------------------------------------------------------

@pytest.fixture(scope="module")
def index() -> dict:
    if not LIB.is_file():
        pytest.skip("PLATE-LIBRARY.json is not built on this checkout")
    return json.loads(LIB.read_text(encoding="utf-8"))


def test_the_count_is_the_back_catalogue_plus_the_probes_one_new_plate(index):
    assert index["count"] == len(index["plates"]) == 329   # + P61 T14: world-tokyo-customs-dock-v1-alive (E99 s55)
    assert sum(1 for p in index["plates"] if p.get("layers")) == 3   # + the alive twin of the dock (P61 T14)


def test_every_record_keeps_every_field_it_had_and_reads_flat_or_layered(index):
    for p in index["plates"]:
        assert BASE_FIELDS <= set(p), p["id"]
        assert bool(p.get("layers")) ^ bool(p.get("flat")), p["id"]
    flat = [p for p in index["plates"] if p.get("flat")]
    assert len(flat) == 326
    assert all(p["flat_reason"] == L.FLAT_BACK_CATALOGUE for p in flat)


def test_the_two_probe_plates_declare_four_split_layers_each(index):
    by_id = {p["id"]: p for p in index["plates"]}
    for plate_id in ("world-banker-apartment-v2", "world-tokyo-customs-dock-v1"):
        layers = by_id[plate_id]["layers"]
        assert [l["role"] for l in layers] == list(ROLES)
        assert [l["depth"] for l in layers] == [1.0, 1.15, 1.275, 1.40]
        assert all(l["generator"] == "depth-split-sam" for l in layers)
        assert all(Path(l["file"]).is_file() for l in layers)
        assert all(l["alpha"] is (l["role"] != "background") for l in layers)


def test_the_new_dock_plate_is_registered_as_a_plate_the_operator_has_not_approved(index):
    dock = {p["id"]: p for p in index["plates"]}["world-tokyo-customs-dock-v1"]
    assert Path(dock["path"]) == DOCK and DOCK.is_file()
    assert dock["register"] == "woodblock-vox-newsprint" and dock["channel"] == "money-physics"
    assert dock["source"] == "p58-probe" and dock["generator"] == "gpt-image-2.0"
    assert "customs" in dock["semantic"] and "crane" in dock["semantic"]
    assert dock["state"] == "review_only" and dock["render_eligible"] is False


def test_the_one_hand_appended_record_a_rebuild_was_dropping_is_carried_forward(index):
    """Found rebuilding for this slice: `plate-p-viewers-desk` was in the shipped index and no
    scanner reproduced it, so every rebuild silently lost an operator-approved, render-eligible
    plate. It is registered now (`assets/plates/plates.json` may NAME a plate that lives elsewhere
    in the project) with its fields and its approval unchanged."""
    desk = {p["id"]: p for p in index["plates"]}["plate-p-viewers-desk"]
    assert Path(desk["path"]).is_file() and desk["path"].endswith("still-p-viewers-desk.png")
    assert desk["state"] == "approved" and desk["render_eligible"] is True
    assert desk["register"] == "stick-on-cream" and desk["flat"] is True


def test_no_probe_layer_png_is_itself_a_record(index):
    paths = {str(Path(p["path"]).resolve()).lower() for p in index["plates"]}
    layers = {str(Path(l["file"]).resolve()).lower()
              for p in index["plates"] for l in p.get("layers", [])}
    assert layers and not (paths & layers)


def test_the_banker_sidecar_keeps_the_plate_it_sits_beside(index):
    assert BANKER.is_file()
    side = BANKER.with_suffix(L.LAYERS_SUFFIX)
    assert side.is_file()
    body = json.loads(side.read_text(encoding="utf-8"))
    assert set(body) >= {"layers"} and isinstance(body["layers"], list)


# ---- E99 s55 (P61 T14): THE ALIVE PLANE - the background WALL is a clip -------------------------
# The operator, 2026-09-16, closing R26-133: *"i think we need both the drift painted as an option and the alive"*,
# then *"when you ran vace did you also run the rest of our depth stack etc?"* The composition's home is this
# sidecar: one layer whose file is an .mp4. Everything else - the parallax planes, the camera at each k, the drift -
# already composes over a background, so nothing new is asked of it. What IS asked is traceability: an alive plane
# that cannot name the still it was pinned to, the region the model was allowed to touch, and the job that made it,
# is an unattributable video, which E10 and E98 s6 both forbid.
ALIVE = (PROJECTS / "tokyo-tea-break/assets/plates/world-tokyo-customs-dock-v1-alive.png")


def _alive_entry(tmp_path: Path, **over) -> dict:
    (tmp_path / "wall.mp4").write_bytes(bytes([0, 0, 0, 24]) + b"ftypmp42")     # the suffix is what makes it a clip
    _png(tmp_path / "wall-still.png", alpha=False)
    _png(tmp_path / "wall-mask.png", alpha=False)
    (tmp_path / "wall.job.json").write_text(json.dumps(
        {"backend": "vace", "model": "wan2.1_vace_1.3B_fp16.safetensors", "width": 480, "height": 320,
         "num_frames": 65, "fps": 16, "cfg": 4.5, "steps": 25, "seed": 4242, "prompt": "harbour water"}),
        encoding="utf-8")
    e = {"path": "wall.mp4", "role": "background", "alpha": False, "generator": "vace",
         "life": {"still": "wall-still.png", "mask": "wall-mask.png", "job": "wall.job.json"}}
    e.update(over)
    return e


def test_an_alive_plane_is_a_clip_with_its_life_recorded(tmp_path):
    entries = [_alive_entry(tmp_path)] + _planes(tmp_path, roles=("mid", "subject", "occluder"))
    layers = L.plate_depth_layers(_plate(tmp_path, entries))
    wall = layers[0]
    assert wall["clip"] is True and wall["role"] == "background" and wall["depth"] == 1.0
    assert wall["generator"] == "vace"
    assert set(wall["life"]) >= {"still", "mask", "job", "settings"}
    assert Path(wall["life"]["still_file"]).is_file() and Path(wall["life"]["job_file"]).is_file()
    assert wall["life"]["settings"]["seed"] == 4242 and wall["life"]["settings"]["cfg"] == 4.5
    assert wall["life"]["settings"]["backend"] == "vace"
    assert all("clip" not in l for l in layers[1:]), "a still plane is untouched by any of this"


def test_every_way_an_alive_plane_goes_wrong_is_refused_by_name(tmp_path):
    still = _planes(tmp_path, roles=("mid", "subject", "occluder"))
    def refuse(**over) -> str:
        return _refusal(tmp_path, [_alive_entry(tmp_path, **over)] + still)
    assert "carries no 'life' record" in refuse(life=None)
    assert "life.mask is missing" in refuse(life={"still": "wall-still.png", "job": "wall.job.json"})
    assert "is not on disk" in refuse(life={"still": "nope.png", "mask": "wall-mask.png", "job": "wall.job.json"})
    assert "an alive plane's generator is one of" in refuse(generator="depth-split")
    assert "a generated clip carries no transparency" in refuse(alpha=True)
    # a clip at any role but the wall: the lane pins everything outside its region to the still
    _png(tmp_path / "world-fixture-v1-background.png", alpha=False)
    wall = {"path": "world-fixture-v1-background.png", "role": "background", "alpha": False,
            "generator": "depth-split-sam"}
    msg = _refusal(tmp_path, [wall, _alive_entry(tmp_path, role="mid", alpha=False)])
    assert "is a CLIP plane at role 'mid'" in msg


def test_the_tokyo_dock_ships_an_alive_twin_and_the_index_carries_it(index):
    """The plate P61 T14 registered: the same layered dock, its wall alive. The mp4 is gitignored
    (E99 s31) - what is committed is this sidecar, the life mask and the generator's job JSON."""
    assert ALIVE.is_file(), "the alive plate's own still is missing - run build_plate_library.py"
    rec = {p["id"]: p for p in index["plates"]}["world-tokyo-customs-dock-v1-alive"]
    roles = [l["role"] for l in rec["layers"]]
    assert roles == ["background", "mid", "subject", "occluder"]
    wall = rec["layers"][0]
    assert wall["clip"] is True and wall["generator"] == "vace"
    assert wall["file"].endswith(".mp4") and Path(wall["file"]).is_file()
    assert wall["life"]["settings"]["seed"] == 4242
    assert rec["state"] == "review_only" and rec["render_eligible"] is False

