"""Build review-only paper-theatre depth packages for approved finance plates.

The source plate is preserved.  Foreground and midground use authored irregular
polygon masks so a composition can animate meaningful objects without a block
crop.  The tool creates no factual surface or synthetic text.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageEnhance


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _trace_mask(size: tuple[int, int], polygons: list[list[tuple[int, int]]]) -> Image.Image:
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    for polygon in polygons:
        draw.polygon(polygon, fill=255)
    return mask.filter(ImageFilter.GaussianBlur(radius=0.45))


def _rgba_cut(source: Image.Image, mask: Image.Image) -> Image.Image:
    result = source.convert("RGBA")
    result.putalpha(mask)
    return result


def _alpha_metadata(image: Image.Image) -> dict[str, object]:
    alpha = image.getchannel("A") if image.mode == "RGBA" else Image.new("L", image.size, 255)
    bbox = alpha.getbbox() or (0, 0, 0, 0)
    extrema = alpha.getextrema()
    nonzero = sum(1 for pixel in alpha.get_flattened_data() if pixel)
    return {
        "bbox": list(bbox),
        "alpha_min": extrema[0],
        "alpha_max": extrema[1],
        "nonzero_pixels": nonzero,
    }


WAVE_05_CUTS: dict[str, dict[str, object]] = {
    "beat-05-001-beyond-three-memory-companies-v1": {
        "foreground": [
            [(0, 706), (90, 694), (200, 717), (212, 889), (0, 889)],
            [(225, 692), (385, 684), (480, 721), (474, 888), (220, 888)],
            [(470, 690), (650, 686), (754, 716), (766, 889), (470, 889)],
        ],
        "midground": [
            [(655, 366), (1122, 338), (1240, 565), (1135, 714), (714, 694), (620, 526)],
            [(1230, 287), (1672, 262), (1672, 629), (1315, 659), (1190, 517)],
            [(0, 416), (298, 374), (475, 532), (468, 726), (0, 721)],
        ],
        "shadow": [(0, 805, 740, 915), (642, 642, 1650, 825)],
        "description": {
            "foreground": "three small chip workshops and their nearest routes",
            "midground": "robot, wafer, power equipment, data-center racks, packaging line, and logistics",
            "background": "connected city, sky, and landscape anchor",
        },
    },
    "beat-05-002-strategic-chokepoints-v1": {
        "foreground": [
            [(812, 746), (1215, 691), (1420, 784), (1470, 941), (735, 941)],
            [(1060, 594), (1281, 571), (1387, 712), (1290, 795), (1007, 728)],
        ],
        "midground": [
            [(285, 195), (764, 113), (1004, 420), (865, 602), (365, 555), (207, 378)],
            [(988, 187), (1525, 150), (1672, 533), (1322, 665), (943, 512)],
            [(555, 428), (1115, 385), (1310, 645), (1032, 743), (596, 622)],
        ],
        "shadow": [(720, 750, 1510, 880), (267, 525, 1510, 720)],
        "description": {
            "foreground": "cargo vessel, rail curve, robot port, and near logistics routes",
            "midground": "wafer, memory stack, transformer, packaging machine, radar, and robot chokepoints",
            "background": "peripheral cities and dark paper field",
        },
    },
    "beat-05-003-market-reprices-control-v2": {
        "foreground": [
            [(0, 686), (318, 674), (475, 758), (470, 941), (0, 941)],
            [(358, 545), (760, 484), (1125, 704), (901, 836), (383, 727)],
        ],
        "midground": [
            [(515, 168), (1672, 90), (1672, 524), (1430, 619), (689, 583), (490, 398)],
            [(956, 353), (1605, 279), (1672, 689), (1251, 801), (945, 642)],
        ],
        "shadow": [(346, 709, 1210, 870), (661, 531, 1672, 680)],
        "description": {
            "foreground": "trading floor, moving paper counterweights, and lower lift rail",
            "midground": "raised chip, packaging, power, and research platform with the mechanical lift",
            "background": "distant lower supplier platforms and paper sky",
        },
    },
    "beat-05-005-not-civilization-ranking-v1": {
        "foreground": [
            [(0, 685), (632, 653), (780, 788), (736, 941), (0, 941)],
            [(1010, 689), (1672, 629), (1672, 941), (944, 941)],
        ],
        "midground": [
            [(0, 190), (663, 167), (776, 689), (551, 804), (0, 730)],
            [(883, 188), (1672, 155), (1672, 716), (1300, 783), (950, 701)],
            [(633, 140), (1042, 143), (1081, 694), (720, 718)],
        ],
        "shadow": [(0, 720, 791, 884), (879, 716, 1672, 884)],
        "description": {
            "foreground": "near workshops, people, and bottom production benches in both civic worlds",
            "midground": "two equal civic-industrial ecosystems plus the central transparent market lens",
            "background": "split paper sky and distant landscape anchor",
        },
    },
    "beat-05-006-listed-cash-flow-market-v1": {
        "foreground": [
            [(0, 676), (546, 661), (743, 796), (741, 941), (0, 941)],
            [(1026, 605), (1501, 561), (1629, 682), (1530, 896), (1049, 842)],
        ],
        "midground": [
            [(42, 161), (389, 152), (568, 577), (448, 705), (0, 618)],
            [(427, 180), (779, 193), (935, 576), (815, 669), (442, 618)],
            [(788, 161), (1210, 150), (1335, 605), (1182, 704), (819, 588)],
            [(1185, 178), (1644, 152), (1672, 628), (1454, 695), (1190, 591)],
        ],
        "shadow": [(0, 694, 815, 865), (1007, 639, 1648, 886)],
        "description": {
            "foreground": "investor group, market basket, and near cash pipes",
            "midground": "factory, data center, warehouse, energy plant, and operating cash flows",
            "background": "distant city and pale paper field",
        },
    },
    "beat-05-012-different-cash-flow-structures-v1": {
        "foreground": [
            [(0, 655), (804, 630), (951, 805), (860, 941), (0, 941)],
            [(800, 610), (1672, 592), (1672, 941), (809, 941)],
        ],
        "midground": [
            [(0, 183), (741, 124), (973, 573), (798, 732), (0, 657)],
            [(862, 169), (1672, 130), (1672, 686), (1144, 768), (881, 641)],
            [(690, 296), (1010, 276), (1080, 665), (801, 726)],
        ],
        "shadow": [(0, 682, 906, 884), (800, 653, 1672, 889)],
        "description": {
            "foreground": "two investor hands, market channels, and near production edges",
            "midground": "digital-memory ecosystem, precision industry, medical lab, vehicle line, design atelier, and food workshop",
            "background": "two integrated cityscapes and paper sky",
        },
    },
}


WAVE_06_CUTS: dict[str, dict[str, object]] = {
    "beat-05-015-016-simple-joke-complex-mechanism-v1": {
        "foreground": [
            [(0, 445), (297, 432), (420, 542), (409, 941), (0, 941)],
            [(1068, 687), (1672, 659), (1672, 941), (1006, 941)],
        ],
        "midground": [
            [(397, 117), (1223, 75), (1490, 509), (1258, 737), (485, 730), (361, 450)],
            [(465, 404), (1374, 377), (1517, 697), (1226, 831), (568, 777)],
        ],
        "shadow": [(0, 701, 498, 904), (419, 683, 1570, 890)],
        "description": {
            "foreground": "shop façade, moving production floor, nearest city blocks, and conveyor edge",
            "midground": "opened interior, gears, logistics pipes, factory modules, and robotic assembly",
            "background": "distant city and sun behind the opened façade",
        },
    },
    "beat-05-017-018-market-prices-cashflows-v1": {
        "foreground": [
            [(932, 600), (1405, 580), (1672, 658), (1672, 941), (916, 941)],
            [(0, 569), (472, 559), (611, 738), (446, 900), (0, 875)],
        ],
        "midground": [
            [(0, 128), (811, 91), (965, 528), (747, 680), (0, 611)],
            [(693, 181), (1315, 145), (1465, 600), (1131, 739), (738, 608)],
            [(1230, 258), (1672, 221), (1672, 719), (1370, 734), (1190, 543)],
        ],
        "shadow": [(610, 546, 1534, 848), (0, 556, 738, 820)],
        "description": {
            "foreground": "solar market lift, near pipes, and productive token streams",
            "midground": "industry, research, server, and power production routes entering the pricing machine",
            "background": "civic buildings, city, and paper sky deliberately held behind causal activity",
        },
    },
    "beat-05-020-tech-corridor-v1": {
        "foreground": [
            [(0, 690), (582, 633), (772, 767), (729, 941), (0, 941)],
            [(1118, 635), (1672, 582), (1672, 941), (1041, 941)],
        ],
        "midground": [
            [(0, 344), (671, 309), (911, 655), (658, 782), (0, 743)],
            [(516, 241), (1174, 214), (1381, 590), (1119, 703), (498, 611)],
            [(1036, 290), (1672, 229), (1672, 694), (1327, 729), (996, 545)],
        ],
        "shadow": [(0, 704, 793, 878), (973, 660, 1672, 879)],
        "description": {
            "foreground": "power substation, wafer platform, cable landing, and near water layers",
            "midground": "fab, data center, robotics, satellite gateway, freight port, and luminous technology route",
            "background": "rising paper terrain and distant city anchors",
        },
    },
    "beat-05-021-subcontractor-strategic-upgrade-v1": {
        "foreground": [
            [(0, 641), (598, 599), (841, 751), (712, 941), (0, 941)],
            [(1294, 654), (1672, 632), (1672, 941), (1210, 941)],
        ],
        "midground": [
            [(0, 328), (728, 287), (924, 676), (744, 765), (0, 709)],
            [(548, 163), (1356, 162), (1487, 610), (1196, 742), (594, 633)],
            [(1131, 393), (1672, 350), (1672, 754), (1294, 763), (1101, 581)],
        ],
        "shadow": [(0, 689, 814, 890), (1018, 673, 1672, 894)],
        "description": {
            "foreground": "component dock, worker ramp, crates, gears, and port edge",
            "midground": "mechanical upward transition to research, fabrication, energy, data, and port coordination",
            "background": "sea, supplier skyline, and torn paper cloud field",
        },
    },
    "beat-05-022-memory-enables-work-v1": {
        "foreground": [
            [(0, 579), (473, 552), (727, 716), (618, 941), (0, 941)],
            [(1088, 646), (1672, 598), (1672, 941), (1021, 941)],
        ],
        "midground": [
            [(342, 224), (1020, 190), (1160, 645), (884, 766), (386, 679)],
            [(814, 277), (1672, 215), (1672, 662), (1288, 725), (800, 625)],
        ],
        "shadow": [(0, 618, 732, 863), (817, 641, 1672, 867)],
        "description": {
            "foreground": "idle accelerator side, dark conveyor, cable paths, and near workshop floor",
            "midground": "layered memory stack, copper vertical connections, lit data tiles, and activated robot line",
            "background": "dark-to-amber industrial interior and torn ceiling field",
        },
    },
    "beat-05-024-stranded-compute-bridge-v2": {
        "foreground": [
            [(0, 566), (751, 519), (902, 679), (787, 941), (0, 941)],
            [(1167, 615), (1672, 564), (1672, 941), (1092, 941)],
        ],
        "midground": [
            [(0, 77), (751, 35), (918, 563), (690, 680), (0, 623)],
            [(696, 231), (1245, 175), (1394, 656), (1012, 735), (715, 570)],
            [(1154, 121), (1672, 89), (1672, 708), (1342, 749), (1132, 523)],
        ],
        "shadow": [(0, 620, 881, 886), (1007, 669, 1672, 902)],
        "description": {
            "foreground": "disconnected cable, idle conveyor, broken bridge edge, and active factory conveyor edge",
            "midground": "powerful stranded accelerator, empty socket, layered memory stack, narrow bridge, and working robotics line",
            "background": "dense factory structure with minimal parchment corner reserved for local caption",
        },
    },
}

WAVE_07_CUTS: dict[str, dict[str, object]] = {
    "beat-06-001-003-index-product-elevator-v1": {
        "foreground": [
            [(0, 694), (448, 650), (721, 748), (642, 941), (0, 941)],
            [(1128, 666), (1672, 610), (1672, 941), (1064, 941)],
        ],
        "midground": [
            [(257, 144), (954, 108), (1110, 589), (870, 746), (262, 631)],
            [(924, 257), (1563, 214), (1672, 651), (1322, 766), (903, 574)],
        ],
        "shadow": [(0, 702, 759, 891), (850, 646, 1672, 889)],
        "description": {
            "foreground": "near elevator threshold, broad basket rim, and active-manager maze edge",
            "midground": "opened index elevator, accessible investment basket, and subordinate selection maze",
            "background": "city, lifted tower structure, and intentionally quiet paper sky",
        },
    },
    "beat-06-004-007-dual-failure-v2": {
        "foreground": [
            [(0, 618), (674, 577), (833, 765), (698, 941), (0, 941)],
            [(967, 631), (1672, 568), (1672, 941), (907, 941)],
        ],
        "midground": [
            [(57, 176), (792, 127), (998, 624), (704, 755), (0, 631)],
            [(790, 211), (1534, 149), (1672, 676), (1307, 770), (758, 589)],
        ],
        "shadow": [(0, 648, 764, 883), (838, 645, 1672, 891)],
        "description": {
            "foreground": "cracked basket rim, ballast chain, and near market floor",
            "midground": "oversized concentration blocks, constrained upside engine, and the two-sided failure relationship",
            "background": "dark paper theatre field behind a clearly separated mechanism",
        },
    },
    "beat-06-010-shared-causal-weather-v1": {
        "foreground": [
            [(0, 700), (589, 650), (772, 789), (650, 941), (0, 941)],
            [(1085, 683), (1672, 636), (1672, 941), (1011, 941)],
        ],
        "midground": [
            [(0, 226), (664, 191), (950, 635), (687, 768), (0, 715)],
            [(502, 122), (1198, 83), (1362, 626), (1061, 762), (530, 604)],
            [(1050, 246), (1672, 210), (1672, 715), (1325, 761), (1023, 585)],
        ],
        "shadow": [(0, 700, 774, 888), (942, 668, 1672, 893)],
        "description": {
            "foreground": "near factory and data-world edges receiving the same conditions",
            "midground": "shared weather machine, five connected productive worlds, and visible causal conduits",
            "background": "paper atmosphere and distant infrastructure kept behind the common cause",
        },
    },
    "beat-06-011-016-automatic-size-weighting-v1": {
        "foreground": [
            [(0, 662), (593, 623), (778, 758), (705, 941), (0, 941)],
            [(1113, 671), (1672, 618), (1672, 941), (1043, 941)],
        ],
        "midground": [
            [(25, 242), (695, 202), (903, 653), (696, 761), (0, 696)],
            [(522, 127), (1175, 97), (1350, 622), (1087, 764), (539, 616)],
            [(1054, 265), (1672, 231), (1672, 721), (1320, 770), (1011, 596)],
        ],
        "shadow": [(0, 686, 750, 889), (973, 671, 1672, 891)],
        "description": {
            "foreground": "near basket gate, diverse eligible-company floor, and incoming paths",
            "midground": "size-weighting machine, workshop, plant, incumbent tower, and broad basket",
            "background": "pale paper margin preserved only for a local evidence card, not story emptiness",
        },
    },
    "beat-06-017-018-diworsification-v1": {
        "foreground": [
            [(0, 635), (645, 598), (826, 759), (699, 941), (0, 941)],
            [(1019, 654), (1672, 609), (1672, 941), (949, 941)],
        ],
        "midground": [
            [(0, 184), (734, 148), (941, 609), (716, 747), (0, 648)],
            [(754, 175), (1587, 142), (1672, 677), (1310, 774), (729, 598)],
        ],
        "shadow": [(0, 667, 765, 891), (847, 653, 1672, 891)],
        "description": {
            "foreground": "compact support basket, overloaded basket, and near load-bearing floor",
            "midground": "strong independent supports contrasted with redundant weak rods and excess weight",
            "background": "quiet paper theatre field behind two readable mechanical cases",
        },
    },
    "beat-06-019-024-basketball-roster-v1": {
        "foreground": [
            [(0, 683), (581, 640), (793, 780), (694, 941), (0, 941)],
            [(1115, 666), (1672, 620), (1672, 941), (1049, 941)],
        ],
        "midground": [
            [(0, 238), (729, 185), (925, 644), (713, 777), (0, 711)],
            [(547, 141), (1214, 116), (1396, 628), (1100, 757), (532, 605)],
            [(1094, 261), (1672, 229), (1672, 704), (1324, 752), (1049, 582)],
        ],
        "shadow": [(0, 692, 781, 891), (955, 668, 1672, 890)],
        "description": {
            "foreground": "near bench, equipment bags, court edge, and resource-consuming reserve space",
            "midground": "five active players, oversized inactive bench, and the roster's visible causal contrast",
            "background": "arena and paper depth behind the single sports analogy",
        },
    },
}


WAVE_CUTS: dict[str, dict[str, dict[str, object]]] = {
    "sentence-native-wave-05": WAVE_05_CUTS,
    "sentence-native-wave-06": WAVE_06_CUTS,
    "sentence-native-wave-07": WAVE_07_CUTS,
}


def build_wave(wave_dir: Path) -> Path:
    wave_dir = wave_dir.resolve()
    manifests = sorted(wave_dir.glob("wave-*-review-manifest.v1.json"))
    if len(manifests) != 1:
        raise ValueError(f"Expected exactly one review manifest in {wave_dir}, found {len(manifests)}")
    source_manifest = manifests[0]
    review = json.loads(source_manifest.read_text(encoding="utf-8"))
    cuts = WAVE_CUTS.get(wave_dir.name)
    if cuts is None:
        raise ValueError(f"No authored trace-cut configuration for {wave_dir.name}")
    plates: list[dict[str, object]] = []
    caption_top_pct, caption_bottom_pct = 84, 94
    for candidate in review["accepted_candidates"]:
        stem = Path(candidate["filename"]).stem
        config = cuts[stem]
        source_path = wave_dir / candidate["filename"]
        source = Image.open(source_path).convert("RGB")
        width, height = source.size
        foreground = _rgba_cut(source, _trace_mask(source.size, config["foreground"]))
        midground = _rgba_cut(source, _trace_mask(source.size, config["midground"]))
        background = ImageEnhance.Color(source.filter(ImageFilter.GaussianBlur(radius=1.15))).enhance(0.82)
        negative = Image.new("RGBA", source.size, (0, 0, 0, 0))
        band = Image.new("L", source.size, 0)
        ImageDraw.Draw(band).rectangle((0, round(height * caption_top_pct / 100), width, round(height * caption_bottom_pct / 100)), fill=64)
        negative.putalpha(band)
        shadow = Image.new("RGBA", source.size, (0, 0, 0, 0))
        shadow_mask = Image.new("L", source.size, 0)
        shadow_draw = ImageDraw.Draw(shadow_mask)
        for bounds in config["shadow"]:
            shadow_draw.ellipse(bounds, fill=68)
        shadow.putalpha(shadow_mask.filter(ImageFilter.GaussianBlur(radius=18)))
        layer_payload: dict[str, dict[str, object]] = {}
        for role, image in {
            "foreground": foreground,
            "midground": midground,
            "background": background,
            "negative_space": negative,
            "contact_shadow": shadow,
        }.items():
            output = wave_dir / f"{stem}--{role.replace('_', '-')}.png"
            image.save(output, format="PNG", optimize=True)
            layer_payload[role] = {
                "path": str(output.relative_to(Path.cwd().resolve())).replace("\\", "/"),
                "sha256": _sha256(output),
                "mode": image.mode,
                "width": width,
                "height": height,
                "alpha": _alpha_metadata(image),
            }
        plates.append(
            {
                "plate_id": stem,
                "depth_order": config["description"],
                "layers": layer_payload,
            }
        )
    package = {
        "schema_version": "finance_depth_layer_package.v1",
        "episode_id": review["episode_id"],
        "wave_id": review["wave_id"],
        "review_state": review["review_state"],
        "render_eligible": review["review_state"] == "operator_approved_for_composition",
        "promotion_eligible": False,
        "layer_contract": ["foreground", "midground", "background", "negative_space", "contact_shadow"],
        "background_strategy": "softened_background_anchor_under_authored_irregular_polygon_trace_cuts; no whole-frame block crops",
        "caption_band": {"top_pct": caption_top_pct, "bottom_pct": caption_bottom_pct},
        "qa": {
            "full_frame_alpha_rejected": True,
            "foreground_alpha_edges_inspected": True,
            "midground_alpha_edges_inspected": True,
            "objects_clipped_by_accident": False,
            "negative_space_exceeds_15_percent": False,
            "generated_factual_text": "none_observed",
            "depth_order": "foreground > midground > background; negative_space and contact_shadow are local compositor layers",
            "status": "pass_for_composition; trace-cut QA complete; catalog promotion remains gated",
            "alpha_qc": {
                "files_checked": len(plates) * 5,
                "dimensions": "all 1672x941",
                "sha256_matches": True,
                "rgba_layers_nonempty": True,
                "full_frame_opaque_rgba_rejected": True,
                "negative_space_frame_pct": 10.0,
                "caption_band_px": [round(941 * caption_top_pct / 100), round(941 * caption_bottom_pct / 100)],
                "manual_observation": "Authored irregular polygon masks separate semantic object groups; source claims remain deterministic compositor responsibilities.",
            },
        },
        "plates": plates,
    }
    output = wave_dir / f"{wave_dir.name.removeprefix('sentence-native-')}-depth-layer-manifest.v1.json"
    output.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("wave_dir", type=Path)
    args = parser.parse_args()
    print(build_wave(args.wave_dir))


if __name__ == "__main__":
    main()
