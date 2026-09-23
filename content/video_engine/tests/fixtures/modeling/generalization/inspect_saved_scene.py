"""Read structured state from an already reopened T4c .blend."""

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def world_location(obj):
    return [round(value, 6) for value in obj.matrix_world.translation]


def top_z(obj):
    return max((obj.matrix_world @ Vector(corner)).z for corner in obj.bound_box)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    if not args.output.is_absolute() or not bpy.data.filepath:
        raise ValueError("reopened blend and absolute output path required")
    scene = bpy.context.scene
    objects = {obj.name: obj for obj in scene.objects}
    report = {
        "source": bpy.data.filepath,
        "blender_version": bpy.app.version_string,
        "fixture_kind": scene.get("fixture_kind"),
        "status": scene.get("status"),
        "resolution_px": [scene.render.resolution_x, scene.render.resolution_y],
        "objects": sorted(objects),
        "armature_objects": sorted(obj.name for obj in objects.values() if obj.type == "ARMATURE"),
    }
    if report["fixture_kind"] == "hinged_prop":
        hinge = objects["Hinge_Pivot"]
        socket = objects["Socket_Grip"]
        lid = objects["Prop_Lid"]
        angles = {}
        for frame in (1, 25):
            scene.frame_set(frame)
            angles[str(frame)] = round(math.degrees(hinge.rotation_euler.x), 6)
        report.update({
            "hinge_angles_deg": angles,
            "hinge_action_present": bool(hinge.animation_data and hinge.animation_data.action),
            "lid_parent": lid.parent.name if lid.parent else None,
            "socket_parent": socket.parent.name if socket.parent else None,
            "socket_id": socket.get("socket_id"),
            "socket_world_location_m": world_location(socket),
        })
    else:
        floor = objects["Floor_Collision"]
        report.update({
            "floor_top_z_m": round(top_z(floor), 6),
            "floor_collision_role": floor.get("collision_role"),
            "floor_surface_id": floor.get("surface_id"),
            "floor_has_collision_modifier": any(mod.type == "COLLISION" for mod in floor.modifiers),
            "layers": {
                obj.name: {"role": obj.get("layer_role"), "depth_y_m": round(obj.matrix_world.translation.y, 6)}
                for obj in objects.values() if obj.get("layer_role")
            },
        })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
