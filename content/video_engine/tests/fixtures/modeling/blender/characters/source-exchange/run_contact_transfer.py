"""Run the opt-in contact-transfer proof inside the pinned Blender runtime."""

import json
import importlib.util
from pathlib import Path
import sys
from types import ModuleType

import bpy


CODE_ROOT = Path(__file__).resolve().parents[8]
MODULE_PATH = CODE_ROOT / "content/video_engine/src/modeling/blender/fight_motion.py"
PACKAGE_NAME = "model_fight_motion_optin"
package = ModuleType(PACKAGE_NAME)
package.__path__ = [str(MODULE_PATH.parent)]
sys.modules[PACKAGE_NAME] = package
spec = importlib.util.spec_from_file_location(PACKAGE_NAME + ".fight_motion", MODULE_PATH)
assert spec and spec.loader
fight_motion = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = fight_motion
spec.loader.exec_module(fight_motion)


args = sys.argv[sys.argv.index("--") + 1:]
if args[0] == "build" and len(args) == 4:
    _, source_root, output, render = args
    source_root = Path(source_root).resolve()
    fixture = source_root / fight_motion.FIXTURE_RELATIVE
    review_root = CODE_ROOT / fight_motion.REVIEW_RELATIVE
    result = fight_motion.build_contact_transfer_exchange(
        bpy, source_root, fixture, Path(output), render=render == "render",
        review_root=review_root,
    )
    print("CONTACT_TRANSFER_JSON=" + json.dumps({
        "status": result["status"],
        "receipt": str(Path(output) / "receipt.json"),
        "scene": result["scene"],
        "checks": result["metrics"]["checks"],
    }, sort_keys=True))
elif args[0] == "reopen" and len(args) == 4:
    _, source_root, scene, receipt = args
    source_root = Path(source_root).resolve()
    try:
        result = fight_motion.reopen_contact_transfer(
            bpy, Path(scene), Path(receipt), root=source_root,
            fixture_path=source_root / fight_motion.FIXTURE_RELATIVE,
            review_root=CODE_ROOT / fight_motion.REVIEW_RELATIVE,
        )
    except fight_motion.FightMotionError as exc:
        print("CONTACT_TRANSFER_REOPEN_REJECTED_JSON=" + json.dumps({"error": str(exc)}))
    else:
        print("CONTACT_TRANSFER_REOPEN_JSON=" + json.dumps(result, sort_keys=True))
else:
    raise ValueError("expected build <source-root> <output> <render|no-render> or "
                     "reopen <source-root> <scene> <receipt>")
