from __future__ import annotations

import hashlib
import json
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

from content.video_engine.console.app import create_app
from content.video_engine.console.settings import load_settings

STYLE = "test-style-v1"


def _png_cutout(path: Path, size=(1024, 1536)) -> str:
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    for y in range(size[1] // 4, 3 * size[1] // 4):
        for x in range(size[0] // 4, 3 * size[0] // 4):
            im.putpixel((x, y), (60, 50, 40, 254))
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _png_world(path: Path, size=(1536, 1024)) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, (240, 230, 200)).save(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _project(tmp_path: Path, *, with_flag: bool = False) -> tuple[TestClient, str]:
    """A project root holding a valid catalogue and a delivery under review."""

    world_sha = _png_world(tmp_path / "assets" / "world-office-v1.png")
    catalog = {
        "schema_version": "finance_asset_catalog.v1",
        "project_root": ".",
        "resolution_order": [
            "exact_semantic_match",
            "reusable_component_composition",
            "deterministic_evidence_or_mechanism",
            "bespoke_plate",
        ],
        "style_families": {"test": [STYLE]},
        "assets": [{
            "asset_id": "world-office-v1",
            "path": "assets/world-office-v1.png",
            "sha256": world_sha,
            "kind": "world_board",
            "style_version": STYLE,
            "semantic_tags": ["office"],
            "visual_worlds": ["story"],
            "identity_lenses": [],
            "resolution_tier": 2,
            "render_eligible": True,
            "review_state": "approved_reusable",
            "placement": {
                "figure_zone": [0.45, 1.0], "baseline_y": 0.98,
                "figure_height": 0.50, "max_figures": 2,
            },
        }],
    }
    (tmp_path / "asset-catalog.v1.json").write_text(json.dumps(catalog), encoding="utf-8")

    delivery = tmp_path / "review" / "batch1"
    clean_sha = _png_cutout(delivery / "actor-clean-v1.png")
    entries = [{
        "asset_id": "actor-clean-v1", "path": "actor-clean-v1.png",
        "sha256": clean_sha, "kind": "actor",
    }]
    if with_flag:
        odd_sha = _png_cutout(delivery / "actor-odd-v1.png", size=(900, 1400))
        entries.append({
            "asset_id": "actor-odd-v1", "path": "actor-odd-v1.png",
            "sha256": odd_sha, "kind": "actor",
        })
    manifest = {"style_family": STYLE, "assets": entries}
    (delivery / "batch1.manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    settings = load_settings(project_root=tmp_path)
    return TestClient(create_app(settings)), str(delivery)


def test_the_triage_screen_renders_filmstrip_stage_and_verdict(tmp_path):
    client, delivery = _project(tmp_path)

    body = client.get("/intake/triage", params={"delivery": delivery}).text

    assert "strip" in body and "stage" in body and "verdict" in body
    assert "/intake/stage.png" in body
    assert "actor-clean-v1" in body


def test_flagged_assets_sort_first_and_carry_no_default(tmp_path):
    client, delivery = _project(tmp_path, with_flag=True)

    body = client.get("/intake/triage", params={"delivery": delivery}).text

    # The flagged asset leads the filmstrip and is the initial selection.
    assert body.index("actor-odd-v1") < body.index("actor-clean-v1")
    assert "(promote)" in body  # the clean asset's default, parenthesised


def test_a_decision_is_stored_and_reversible_until_commit(tmp_path):
    client, delivery = _project(tmp_path, with_flag=True)
    client.get("/intake/triage", params={"delivery": delivery})

    r = client.post("/intake/decide", data={
        "delivery": delivery, "asset_id": "actor-odd-v1", "decision": "reject",
        "next_url": f"/intake/triage?delivery={delivery}",
    }, follow_redirects=False)
    assert r.status_code == 303

    body = client.get("/intake/triage", params={"delivery": delivery}).text
    assert "reject" in body

    client.post("/intake/undo", data={"delivery": delivery, "asset_id": "actor-odd-v1"},
                follow_redirects=False)
    body = client.get("/intake/triage", params={"delivery": delivery}).text
    # Back to no explicit decision: the flag asset shows no decision mark.
    assert ">reject<" not in body


def test_promoting_a_failed_asset_is_refused_with_the_policy_text(tmp_path):
    client, delivery = _project(tmp_path)
    # Break the digest so the asset fails intake.
    manifest_path = Path(delivery) / "batch1.manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["assets"][0]["sha256"] = "a" * 64
    manifest_path.write_text(json.dumps(payload), encoding="utf-8")
    client.get("/intake/triage", params={"delivery": delivery})

    r = client.post("/intake/decide", data={
        "delivery": delivery, "asset_id": "actor-clean-v1", "decision": "promote",
    })

    assert "cannot be promoted" in r.text


def test_no_triage_route_mutates_the_catalogue(tmp_path):
    client, delivery = _project(tmp_path, with_flag=True)
    catalog_path = tmp_path / "asset-catalog.v1.json"
    before = catalog_path.read_bytes()

    client.get("/intake/triage", params={"delivery": delivery})
    client.post("/intake/decide", data={
        "delivery": delivery, "asset_id": "actor-odd-v1", "decision": "reject",
    })
    client.get("/intake/stage.png", params={"delivery": delivery, "asset": "actor-clean-v1"})

    assert catalog_path.read_bytes() == before


def test_the_stage_composites_by_default_and_isolates_on_request(tmp_path):
    client, delivery = _project(tmp_path)
    client.get("/intake/triage", params={"delivery": delivery})

    composite = client.get("/intake/stage.png", params={
        "delivery": delivery, "asset": "actor-clean-v1", "mode": "composite",
    })
    isolated = client.get("/intake/stage.png", params={
        "delivery": delivery, "asset": "actor-clean-v1", "mode": "isolated",
    })

    assert composite.status_code == 200 and isolated.status_code == 200
    # The composite is a 1920-wide placement frame; the isolated view is the raw file.
    from io import BytesIO

    assert Image.open(BytesIO(composite.content)).size == (1920, 1080)
    assert Image.open(BytesIO(isolated.content)).size == (1024, 1536)


def test_the_stage_refuses_a_path_escaping_the_delivery_root(tmp_path):
    client, delivery = _project(tmp_path)
    manifest_path = Path(delivery) / "batch1.manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["assets"].append({
        "asset_id": "actor-escape-v1", "path": "../../asset-catalog.v1.json",
        "sha256": "a" * 64, "kind": "actor",
    })
    manifest_path.write_text(json.dumps(payload), encoding="utf-8")
    client.get("/intake/triage", params={"delivery": delivery})

    r = client.get("/intake/stage.png", params={
        "delivery": delivery, "asset": "actor-escape-v1",
    })

    assert r.status_code == 400


def test_every_key_action_has_a_visible_control(tmp_path):
    """Keyboard-complete: keys are shortcuts to controls that exist on the page."""

    client, delivery = _project(tmp_path)
    body = client.get("/intake/triage", params={"delivery": delivery}).text

    assert 'id="form-promote"' in body
    assert 'id="form-reject"' in body
    assert 'id="form-skip"' in body
    assert 'id="commit-link"' in body
    assert 'id="ground-link"' in body
    assert "console.js" in body


def test_every_url_the_key_layer_reads_is_actually_rendered(tmp_path):
    """Derived, not hand-listed.

    The previous version of this rule was a list a human kept in sync, so a key
    added without its data attribute would sail through. Read the dataset keys
    out of the script instead: a navigation key that reads an attribute the
    server never renders is a silent dead key, which is worse than a broken one.
    """

    import re

    from content.video_engine.console.app import STATIC_DIR

    script = (STATIC_DIR / "console.js").read_text(encoding="utf-8")
    keys = set(re.findall(r"nav\.dataset\.(\w+)", script))
    assert keys, "the key layer reads no dataset attributes; this test is watching nothing"

    client, delivery = _project(tmp_path)
    body = client.get("/intake/triage", params={"delivery": delivery}).text

    # Scope to the element ``nav.dataset`` actually reads. A page-wide substring
    # search passes on an attribute of the same name somewhere else entirely —
    # ``data-ground`` also sits on the stage — and proves nothing.
    element = re.search(r"<div[^>]*id=\"nav-data\"[^>]*>", body)
    assert element, "the key layer's data element is not rendered at all"
    element = element.group(0)

    for key in sorted(keys):
        attribute = "data-" + re.sub(r"(?<!^)(?=[A-Z])", "-", key).lower()
        assert attribute in element, (
            f"console.js reads nav.dataset.{key} but #nav-data does not carry {attribute}"
        )


def test_the_stage_ground_is_paper_by_default_and_survives_navigation(tmp_path):
    """The ground is a URL parameter, so it holds while stepping the filmstrip."""

    client, delivery = _project(tmp_path)

    body = client.get("/intake/triage", params={"delivery": delivery}).text
    assert 'class="stage" data-ground="paper"' in body

    dark = client.get("/intake/triage", params={"delivery": delivery, "ground": "dark"}).text
    assert 'class="stage" data-ground="dark"' in dark
    # Every onward link keeps the operator on the ground they chose.
    assert "ground=paper" not in dark.split('id="ground-link"')[0]


def test_an_unknown_ground_falls_back_rather_than_failing(tmp_path):
    client, delivery = _project(tmp_path)

    body = client.get(
        "/intake/triage", params={"delivery": delivery, "ground": "chartreuse"}
    ).text

    assert 'class="stage" data-ground="paper"' in body
