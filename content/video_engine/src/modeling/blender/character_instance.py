"""Append independently poseable native character trees into a Blender scene.

Called inside Blender; no user add-ons or embedded source scripts are needed.
This is an opt-in technical staging primitive, not character-art approval.
"""

from __future__ import annotations

import hashlib
import math
from pathlib import Path
import re
from typing import Any


_BINDING_ID = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")


class CharacterInstanceError(ValueError):
    """The source or a requested rig/skin binding is unsafe or incomplete."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def append_character_instance(
    bpy: Any,
    *,
    source: Path,
    source_sha256: str,
    binding_id: str,
    rig_name: str,
    object_names: tuple[str, ...],
    position_m: tuple[float, float, float],
    heading_rad: float,
) -> dict[str, Any]:
    """Append one source-local rig tree with private mesh, rig and action data.

    ``object_names`` is an audited render-object allowlist including the rig.
    Every selected mesh must be parented to, or skinned exclusively by, that
    rig. A skinned mesh with no parent (notably the v1.1 shorts shell) is
    attached before root placement so its evaluated geometry travels with the
    actor. Source files are never opened as the active scene or saved.
    """

    if not isinstance(binding_id, str) or not _BINDING_ID.fullmatch(binding_id):
        raise CharacterInstanceError("binding_id must be a safe identifier")
    if not isinstance(rig_name, str) or not rig_name:
        raise CharacterInstanceError("rig_name must be non-empty")
    if (not isinstance(object_names, tuple) or not 2 <= len(object_names) <= 32
            or len(set(object_names)) != len(object_names)
            or rig_name not in object_names
            or any(not isinstance(name, str) or not name for name in object_names)):
        raise CharacterInstanceError("object_names must be a unique audited rig/render allowlist")
    if (not isinstance(position_m, tuple) or len(position_m) != 3
            or any(isinstance(value, bool) or not isinstance(value, (int, float))
                   or not math.isfinite(value) or abs(value) > 100 for value in position_m)
            or isinstance(heading_rad, bool) or not isinstance(heading_rad, (int, float))
            or not math.isfinite(heading_rad)):
        raise CharacterInstanceError("placement must contain bounded finite values")
    source = Path(source)
    if (not source.is_file() or source.is_symlink() or source.suffix.lower() != ".blend"
            or source.stat().st_size < 50_000
            or not re.fullmatch(r"[0-9a-f]{64}", source_sha256)
            or _sha256(source) != source_sha256):
        raise CharacterInstanceError("source blend is missing, redirected or hash-mismatched")
    if bpy.data.collections.get(f"character__{binding_id}") is not None:
        raise CharacterInstanceError(f"binding {binding_id!r} already exists")

    requested = tuple(sorted(object_names))
    with bpy.data.libraries.load(str(source), link=False) as (available, loaded):
        if not set(requested) <= set(available.objects):
            raise CharacterInstanceError("source blend lacks an audited character object")
        # Blender replaces entries in this mutable list with appended datablocks.
        loaded.objects = list(requested)
    if len(loaded.objects) != len(requested):
        raise CharacterInstanceError("Blender returned an incomplete character object list")
    objects = dict(zip(requested, loaded.objects))
    if any(obj is None for obj in objects.values()):
        raise CharacterInstanceError("Blender did not append every character object")
    rig = objects[rig_name]
    if rig.type != "ARMATURE":
        raise CharacterInstanceError("rig_name does not identify an armature")

    for name, obj in objects.items():
        if obj is rig:
            continue
        if obj.type != "MESH":
            raise CharacterInstanceError(f"{name!r} is not an audited render mesh")
        modifiers = [modifier for modifier in obj.modifiers if modifier.type == "ARMATURE"]
        if not modifiers or any(modifier.object is not rig for modifier in modifiers):
            raise CharacterInstanceError(f"{name!r} has a missing or foreign skin rig")
        if obj.parent is not None and obj.parent is not rig:
            raise CharacterInstanceError(f"{name!r} has a foreign parent")

    collection = bpy.data.collections.new(f"character__{binding_id}")
    bpy.context.scene.collection.children.link(collection)
    for name, obj in objects.items():
        obj.name = f"{binding_id}__{name}"
        collection.objects.link(obj)
        original_data = obj.data
        obj.data = obj.data.copy()
        if original_data.users == 0:
            if obj.type == "ARMATURE":
                bpy.data.armatures.remove(original_data)
            else:
                bpy.data.meshes.remove(original_data)
        obj["model_binding_id"] = binding_id
        obj["source_object_name"] = name
        if obj.type == "MESH" and obj.parent is None:
            original_world = obj.matrix_world.copy()
            obj.parent = rig
            obj.matrix_parent_inverse = rig.matrix_world.inverted()
            obj.matrix_world = original_world

    original_action = rig.animation_data.action if rig.animation_data else None
    if original_action is not None:
        rig.animation_data.action = original_action.copy()
        rig.animation_data.action.name = f"{binding_id}__source_action"
        if original_action.users == 0:
            bpy.data.actions.remove(original_action)
    rig.rotation_mode = "XYZ"
    rig.location = position_m
    rig.rotation_euler.z = heading_rad
    bpy.context.view_layer.update()
    if _sha256(source) != source_sha256:
        raise CharacterInstanceError("source blend changed during append")
    return objects
