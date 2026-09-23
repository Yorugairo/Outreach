"""Render saved shorts with unlit material to distinguish lighting from geometry defects."""

import argparse
import sys
from pathlib import Path

import bpy


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    if not args.output.is_absolute():
        raise ValueError("emission probe output must be an absolute path")
    garment = bpy.data.objects.get("Garment_FightShorts")
    camera = bpy.data.objects.get("ReviewCamera_garment_stress")
    if garment is None or camera is None:
        raise RuntimeError("saved garment or stress camera is missing")
    for material in garment.data.materials:
        material.use_nodes = True
        nodes = material.node_tree.nodes
        nodes.clear()
        output = nodes.new("ShaderNodeOutputMaterial")
        emission = nodes.new("ShaderNodeEmission")
        emission.inputs["Color"].default_value = material.diffuse_color
        emission.inputs["Strength"].default_value = 1.0
        material.node_tree.links.new(emission.outputs[0], output.inputs["Surface"])
    scene = bpy.context.scene
    scene.camera = camera
    scene.frame_set(52)
    scene.render.resolution_x = 512
    scene.render.resolution_y = 512
    args.output.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(args.output)
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
