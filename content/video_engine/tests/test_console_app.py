from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from content.video_engine.console.app import STATIC_DIR, TEMPLATE_DIR, create_app
from content.video_engine.console.settings import load_settings

STYLE = "paper-cut-reduced-density-v2"


def _asset(asset_id: str, **over) -> dict:
    asset = {
        "asset_id": asset_id,
        "path": f"assets/generated/cutouts/{asset_id}.png",
        "sha256": "a" * 64,
        "kind": "actor",
        "style_version": STYLE,
        "semantic_tags": ["host"],
        "visual_worlds": ["story"],
        "identity_lenses": ["finance-host"],
        "resolution_tier": 2,
        "render_eligible": False,
        "review_state": "review_only",
    }
    asset.update(over)
    return asset


def _catalog(*assets, **over) -> dict:
    payload = {
        "schema_version": "finance_asset_catalog.v1",
        "project_root": ".",
        "resolution_order": [
            "exact_semantic_match",
            "reusable_component_composition",
            "deterministic_evidence_or_mechanism",
            "bespoke_plate",
        ],
        "assets": list(assets),
    }
    payload.update(over)
    return payload


def _client(tmp_path: Path, catalog: dict | None) -> TestClient:
    if catalog is None:
        return TestClient(create_app(load_settings(env={})))
    path = tmp_path / "asset-catalog.v1.json"
    path.write_text(json.dumps(catalog), encoding="utf-8")
    return TestClient(create_app(load_settings(catalog_path=path)))


def test_catalogue_lists_every_asset_with_its_review_state(tmp_path):
    client = _client(tmp_path, _catalog(
        _asset("actor-host-v1"),
        _asset("world-hall-v1", kind="world_board", render_eligible=True,
               review_state="approved_reusable"),
    ))

    body = client.get("/catalog").text

    assert "actor-host-v1" in body
    assert "world-hall-v1" in body
    assert "review_only" in body
    assert "approved_reusable" in body


def test_an_invalid_catalogue_surfaces_the_service_error_not_a_stack_trace(tmp_path):
    # A world claiming 0.50 whose chair back implies a 0.92 adult: the scale guard
    # in asset_catalog owns this rule, and the console must not restate it.
    bad = _asset(
        "world-office-v1",
        kind="world_board",
        placement={"figure_zone": [0.55, 1.0], "baseline_y": 0.98, "figure_height": 0.50},
        scale_reference={"object": "chair back", "real_height_m": 0.85, "drawn_height": 0.45},
    )
    response = _client(tmp_path, _catalog(bad)).get("/catalog")

    assert response.status_code == 200
    assert "Catalogue rejected" in response.text
    assert "world-office-v1" in response.text
    # 0.45 * (1.75 / 0.85) = 0.93 — the service states what it measured.
    assert "0.93" in response.text, "the service's measured value must reach the operator"
    assert "Traceback" not in response.text


def test_an_unconfigured_console_renders_an_empty_state_rather_than_failing(tmp_path):
    response = _client(tmp_path, None).get("/catalog")

    assert response.status_code == 200
    assert "No catalogue configured" in response.text
    assert "--project-root" in response.text


def test_a_missing_catalogue_file_is_reported_by_path(tmp_path):
    settings = load_settings(catalog_path=tmp_path / "absent.json")
    response = TestClient(create_app(settings)).get("/catalog")

    assert response.status_code == 200
    assert "Catalogue not found" in response.text
    assert "absent.json" in response.text


def test_render_eligibility_is_visible_chrome_not_a_silent_property(tmp_path):
    client = _client(tmp_path, _catalog(
        _asset("actor-a-v1"),
        _asset("actor-b-v1", render_eligible=True, review_state="approved_reusable"),
    ))

    body = client.get("/catalog").text

    # Status carries a text label, never colour alone.
    assert "REVIEW" in body
    assert "RENDER" in body


def test_the_index_serves_the_catalogue(tmp_path):
    assert _client(tmp_path, _catalog(_asset("actor-host-v1"))).get("/").status_code == 200


@pytest.mark.parametrize(
    "path",
    sorted(TEMPLATE_DIR.rglob("*.html"))
    + sorted(STATIC_DIR.rglob("*.css"))
    + sorted(STATIC_DIR.rglob("*.js")),
)
def test_no_template_or_stylesheet_reaches_off_origin(path):
    """The offline guarantee is enforced, not assumed.

    A CDN font or script would make the console fail on a machine with no
    network, which is exactly where it is meant to run.
    """

    source = path.read_text(encoding="utf-8")
    # Strip comments first: prose about not using a CDN is not a CDN reference.
    stripped = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    stripped = re.sub(r"<!--.*?-->", "", stripped, flags=re.DOTALL)
    stripped = re.sub(r"^\s*//.*$", "", stripped, flags=re.MULTILINE)
    offenders = re.findall(r"""(?:https?:)?//[^\s"')]+""", stripped)
    # Protocol-relative or absolute URLs are the failure; site-root paths are fine.
    assert not offenders, f"{path.name} references off-origin: {offenders}"
    assert "@import" not in stripped


def test_the_review_stage_is_lighter_than_the_operator_chrome_around_it():
    """The stage is the delivery ground, not a darkroom.

    An asset judged over near-black reads luminous and ships muddy, so the
    default ground approximates paper while the chrome stays dark. The
    high-contrast ground survives as an opt-in, not as the default.
    """

    css = (STATIC_DIR / "console.css").read_text(encoding="utf-8")
    tokens = dict(re.findall(r"(--[a-z-]+):\s*(#[0-9a-fA-F]{6})", css))

    def luminance(hex_colour: str) -> float:
        r, g, b = (int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5))
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    assert luminance(tokens["--stage"]) > 0.6, "the default stage must read as paper"
    assert luminance(tokens["--surface"]) < 0.2, "operator chrome must stay dark"
    assert luminance(tokens["--stage-dark"]) < 0.2, "the opt-in ground is the dark one"


def test_console_chrome_never_borrows_a_library_colour():
    """Chrome must never be mistaken for art — including the paper stage.

    The stage deliberately sits near the library cream without matching it: an
    exact match would camouflage the cream rim a bad matte leaves behind.
    """

    css = (STATIC_DIR / "console.css").read_text(encoding="utf-8")
    library_palette = ("#f4e6c7", "#25313c", "#1769c2", "#178c83", "#f5b72e", "#ed6a4a")
    lowered = css.lower()
    for colour in library_palette:
        assert lowered.count(colour) == lowered.count(f"({colour}"), (
            f"console chrome must not use the library colour {colour}"
        )


def test_static_assets_are_served(tmp_path):
    assert _client(tmp_path, None).get("/static/console.css").status_code == 200
