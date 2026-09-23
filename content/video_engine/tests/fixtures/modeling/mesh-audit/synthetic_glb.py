"""Small self-contained glTF binary fixtures for the source-neutral mesh audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct
from typing import Any


def _pack_glb(document: dict[str, Any], binary: bytes = b"") -> bytes:
    json_chunk = json.dumps(document, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    json_chunk += b" " * (-len(json_chunk) % 4)
    binary_chunk = binary + b"\x00" * (-len(binary) % 4)
    chunks = struct.pack("<I4s", len(json_chunk), b"JSON") + json_chunk
    if binary_chunk:
        chunks += struct.pack("<I4s", len(binary_chunk), b"BIN\x00") + binary_chunk
    return b"glTF" + struct.pack("<II", 2, 12 + len(chunks)) + chunks


def triangle_glb_bytes() -> bytes:
    positions = struct.pack("<9f", 0, 0, 0, 1, 0, 0, 0, 1, 0)
    uvs = struct.pack("<6f", 0, 0, 1, 0, 0, 1)
    indices = struct.pack("<3H", 0, 1, 2)
    binary = positions + uvs + indices
    document = {
        "asset": {"version": "2.0", "generator": "outreach-model-mesh-audit-fixture"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0, "name": "SyntheticTriangle"}],
        "meshes": [
            {
                "name": "SyntheticTriangleMesh",
                "primitives": [
                    {
                        "attributes": {"POSITION": 0, "TEXCOORD_0": 1},
                        "indices": 2,
                        "material": 0,
                    }
                ],
            }
        ],
        "materials": [
            {
                "name": "SyntheticBlue",
                "pbrMetallicRoughness": {"baseColorFactor": [0.1, 0.2, 0.8, 1.0]},
            }
        ],
        "buffers": [{"byteLength": len(binary)}],
        "bufferViews": [
            {"buffer": 0, "byteOffset": 0, "byteLength": len(positions), "target": 34962},
            {
                "buffer": 0,
                "byteOffset": len(positions),
                "byteLength": len(uvs),
                "target": 34962,
            },
            {
                "buffer": 0,
                "byteOffset": len(positions) + len(uvs),
                "byteLength": len(indices),
                "target": 34963,
            },
        ],
        "accessors": [
            {
                "bufferView": 0,
                "componentType": 5126,
                "count": 3,
                "type": "VEC3",
                "min": [0, 0, 0],
                "max": [1, 1, 0],
            },
            {"bufferView": 1, "componentType": 5126, "count": 3, "type": "VEC2"},
            {"bufferView": 2, "componentType": 5123, "count": 3, "type": "SCALAR"},
        ],
    }
    return _pack_glb(document, binary)


def empty_glb_bytes() -> bytes:
    return _pack_glb(
        {
            "asset": {"version": "2.0", "generator": "outreach-model-mesh-audit-empty-fixture"},
            "scene": 0,
            "scenes": [{"nodes": []}],
        }
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Write the synthetic triangle GLB audit fixture.")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if args.output.exists() and not args.overwrite:
        parser.error("output already exists; pass --overwrite to replace this fixture")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(triangle_glb_bytes())
    print(f"wrote {args.output} ({args.output.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
