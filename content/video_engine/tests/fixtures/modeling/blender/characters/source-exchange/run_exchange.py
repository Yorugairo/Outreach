"""Run the self-contained source exchange builder or reopen check inside Blender."""

import importlib.util
import json
from pathlib import Path
import sys

import bpy


ROOT = Path(__file__).resolve().parents[8]
MODULE_PATH = ROOT / "content/video_engine/src/modeling/blender/fight_motion.py"
spec = importlib.util.spec_from_file_location("model_fight_motion", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

args = sys.argv[sys.argv.index("--") + 1:]
if args[0] == "build" and len(args) == 4:
    _, fixture, output, render = args
    result = module.build_exchange(
        bpy, ROOT, Path(fixture), Path(output), render=render == "render"
    )
    print("FIGHT_MOTION_JSON=" + json.dumps({
        "status": result["status"],
        "receipt": str(Path(output) / "receipt.json"),
        "scene": result["scene"],
        "checks": result["metrics"]["checks"],
    }, sort_keys=True))
elif args[0] == "reopen" and len(args) == 3:
    _, scene, receipt = args
    try:
        result = module.reopen_exchange(bpy, Path(scene), Path(receipt))
    except module.FightMotionError as exc:
        print("FIGHT_REOPEN_REJECTED_JSON=" + json.dumps({"error": str(exc)}, sort_keys=True))
    else:
        print("FIGHT_REOPEN_JSON=" + json.dumps(result, sort_keys=True))
elif args[0] == "remove-armature" and len(args) == 3:
    _, scene, object_name = args
    if "FINISHED" not in bpy.ops.wm.open_mainfile(filepath=scene, load_ui=False, use_scripts=False):
        raise RuntimeError("Blender could not open disposable corruption probe")
    obj = bpy.data.objects.get(object_name)
    if obj is None:
        raise ValueError(f"corruption probe object is missing: {object_name}")
    modifiers = [item for item in obj.modifiers if item.type == "ARMATURE"]
    if not modifiers:
        raise ValueError(f"corruption probe has no Armature modifier: {object_name}")
    for modifier in modifiers:
        obj.modifiers.remove(modifier)
    bpy.ops.wm.save_as_mainfile(filepath=scene, check_existing=False, compress=True)
    print("FIGHT_MOTION_CORRUPTION_JSON=" + json.dumps({
        "object": object_name, "armature_modifiers_removed": len(modifiers),
    }, sort_keys=True))
else:
    raise ValueError(
        "expected build <fixture> <output> <render|no-render>, "
        "reopen <scene> <receipt>, or remove-armature <scene> <object>"
    )
