"""Intake both local .blend sources as review-only model_asset.v1 candidates."""

import argparse
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT))

from content.video_engine.src.modeling.contracts import validate_model_asset, validate_model_scene  # noqa: E402
from content.video_engine.src.modeling.importers import intake_model_bundle  # noqa: E402


SPECS = ROOT / "content/video_engine/assets/modeling/native/generalization/asset-specs.v1.json"


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_diagnostics(source_dir, project_root, contract_dir, render_dir, manifest_path, *, portable=False):
    specs = json.loads(SPECS.read_text(encoding="utf-8"))
    entries = {}
    for kind, spec in specs["assets"].items():
        source = source_dir / spec["source"]
        digest = sha256(source)
        sidecar = source.with_name(source.name + ".dependencies.json")
        sidecar.write_text(json.dumps({"schema_version": "blend_dependencies.v1",
                                       "packed": True, "dependencies": []}, indent=2), encoding="utf-8")
        run_dir = contract_dir / kind / (digest[:12] + "-native")
        receipt = intake_model_bundle(
            source,
            project_root=project_root,
            run_dir=run_dir,
            allowed_source_root=source_dir,
            asset_id=spec["asset_id"],
            revision_id=spec["revision_id"],
            asset_kind=spec["asset_kind"],
            coordinate_system=specs["coordinate_system"],
            capabilities=spec["capabilities"],
            expected_sha256=digest,
            provenance={"authoring_method": "native", "provider_calls": 0},
        )
        descriptor = validate_model_asset(receipt["descriptor_path"], project_root=project_root)
        if descriptor["asset_kind"] != spec["asset_kind"]:
            raise AssertionError(f"asset kind mismatch for {kind}")
        names = (["hinged-prop-closed.png", "hinged-prop-open.png"] if kind == "prop" else
                 ["environment-three-quarter.png", "environment-front.png"])
        entries[kind] = {
            "asset_id": spec["asset_id"],
            "asset_kind": spec["asset_kind"],
            "editable_source": str(source),
            "editable_source_sha256": digest,
            "descriptor_path": receipt["descriptor_path"],
            "descriptor_sha256": sha256(Path(receipt["descriptor_path"])),
            "review_state": "review_only",
            "render_eligible": False,
            "renders": {name: {"path": str(render_dir / name), "sha256": sha256(render_dir / name)} for name in names},
        }
    bindings = []
    for kind, entry in entries.items():
        spec = specs["assets"][kind]
        descriptor = Path(entry["descriptor_path"])
        bindings.append({
            "binding_id": kind,
            "asset_id": spec["asset_id"],
            "revision_id": spec["revision_id"],
            "descriptor_path": descriptor.relative_to(project_root).as_posix(),
            "descriptor_sha256": entry["descriptor_sha256"],
        })
    scene = {
        "schema_version": "model_scene.v1",
        "scene_id": "diagnostic-generalization",
        "duration_frames": 26,
        "fps": {"numerator": 24, "denominator": 1},
        "time_origin": {"scene_frame": 0, "scene_time_seconds": {"numerator": 0, "denominator": 1}},
        "bindings": bindings,
        "participants": [],
        "source_time_mappings": [],
        "contacts": [],
        "events": [{"event_id": "lid-open", "event_type": "articulation", "frame": 25, "binding_id": "prop"}],
        "attachments": [],
        "environment_collision_surfaces": [
            {"binding_id": "environment", "surface_id": "floor", "collision_mode": "solid"}
        ],
        "motion_channels": [{
            "channel_id": "lid-hinge", "binding_id": "prop", "target_kind": "articulation",
            "semantic_target": "lid_hinge", "value_unit": "degrees", "interpolation": "linear",
            "keyframes": [{"frame": 1, "value": 0.0}, {"frame": 25, "value": -74.484511}],
        }],
    }
    validate_model_scene(scene, project_root=project_root)
    scene_path = source_dir / "diagnostic-scene.model_scene.v1.json"
    scene_path.write_text(json.dumps(scene, indent=2, sort_keys=True), encoding="utf-8")
    manifest = {"schema_version": "diagnostic-generalization-manifest.v1",
                "status": "diagnostic_only", "art_approval": "not_approved",
                "blender_version": "5.2.2 LTS", "provider_calls": 0, "assets": entries,
                "scene_binding_path": str(scene_path), "scene_binding_sha256": sha256(scene_path)}
    if portable:
        def relative(path):
            return Path(path).relative_to(project_root).as_posix()

        manifest["scene_binding_path"] = relative(scene_path)
        for kind, entry in entries.items():
            entry["editable_source"] = relative(entry["editable_source"])
            entry["descriptor_path"] = relative(entry["descriptor_path"])
            for render in entry["renders"].values():
                render["path"] = relative(render["path"])
            per_asset = {"schema_version": "diagnostic-model-source.v1",
                         "status": "diagnostic_only", "art_approval": "not_approved",
                         "provider_calls": 0, "blender_version": "5.2.2 LTS", **entry}
            (source_dir / f"{specs['assets'][kind]['asset_id']}.manifest.json").write_text(
                json.dumps(per_asset, indent=2, sort_keys=True), encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--contract-dir", type=Path, required=True)
    parser.add_argument("--render-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--portable-manifest", action="store_true")
    args = parser.parse_args()
    for path in (args.source_dir, args.project_root, args.contract_dir, args.render_dir, args.manifest):
        if not path.is_absolute():
            raise ValueError("absolute paths required")
    result = validate_diagnostics(args.source_dir, args.project_root, args.contract_dir,
                                  args.render_dir, args.manifest, portable=args.portable_manifest)
    print(json.dumps({kind: {"sha256": data["editable_source_sha256"],
                              "descriptor": data["descriptor_path"]}
                      for kind, data in result["assets"].items()}, indent=2))


if __name__ == "__main__":
    main()
