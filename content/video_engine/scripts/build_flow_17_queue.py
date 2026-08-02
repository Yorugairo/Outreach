from __future__ import annotations

import hashlib
import json
from pathlib import Path

SELECTED_ORDERS = [1, 3, 4, 5, 6, 7, 8, 9, 11, 12, 65, 66, 67, 69, 70, 71, 72]
PLATE_BY_ORDER = {
    1: "001.png", 3: "001.png",
    4: "002.png", 5: "002.png",
    6: "003.png", 7: "003.png", 8: "003.png",
    9: "004.png", 11: "004.png",
    12: "005.png",
    65: "031.png", 66: "031.png",
    67: "032.png",
    69: "033.png", 70: "033.png",
    71: "034.png", 72: "034.png",
}

# The handoff defines the cast policy for 1–5 and 6–8/65–72. Orders 9–12
# continue the Kano institutional sequence, so they use the same Kano cast as
# the preceding institutional beats. This is a reversible queue decision only;
# it does not approve or submit generation.
CAST_BY_ORDER = {
    **{order: ["kano-reconstruction", "registry-learner"] for order in [1, 3, 4, 5, 9, 11, 12]},
    **{order: ["maeda-reconstruction", "registry-learner"] for order in [6, 7, 8, 65, 66, 67]},
    **{order: ["brazilian-bridge-composite", "registry-learner"] for order in [69, 70, 71, 72]},
}
CAST_LABELS = {
    "kano-reconstruction": "Kano Reconstruction",
    "maeda-reconstruction": "Maeda Reconstruction",
    "brazilian-bridge-composite": "Brazilian Bridge Composite",
    "registry-learner": "Learner Throughline",
}
ACTION_BY_RECIPE = {
    "parallax_push": "Kano opens a teaching ledger carrying only sparse, non-readable decorative brushwork while the learner watches.",
    "masked_reveal": "A paper mask reveals the named characters in the same quiet training space.",
    "evidence_highlight": "One named character places a teaching ledger with sparse, non-readable decorative brushwork on a table while the learner observes.",
    "map_trace": "A named character traces a route across a blank paper map with no labels or symbols.",
    "comic_pop": "The learner turns toward one period training prop as a paper panel shifts into view.",
    "split_compare": "Two quiet paper panels hold the same named characters and contrasting training props without text.",
    "type_build": "The learner arranges folio panels with sparse, non-readable decorative brush texture on a table; no lettering or symbols appear.",
    "paper_transition": "A paper folio page turns to reveal the same named characters in a restrained training room.",
    "detail_punch": "Close on a named character's hand opening a teaching ledger with sparse, non-readable decorative brushwork while the learner remains in frame.",
}
NEGATIVE = (
    "No generated text, dates, labels, logos, citations, watermarks, extra characters, "
    "camera shake, background pan, photorealism, live action, dialogue, lip sync, "
    "new factual claims, or creator imitation. Do not render any visible writing, "
    "lettering, nameplates, lower thirds, title cards, character labels, or the "
    "names of the attached reference cards; those names are internal production "
    "metadata only. Props may contain sparse, abstract, non-readable decorative "
    "brush texture, but never words, names, dates, labels, diagrams, symbols, "
    "glyph sequences, or readable calligraphy."
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    repo = Path(__file__).resolve().parents[3]
    job = repo / ".context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080"
    plan_path = job / "character-motion-production/producer_plan.with-cast.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    by_order = {int(block["order"]): block for block in plan["blocks"]}
    errors: list[str] = []
    items: list[dict[str, object]] = []

    for order in SELECTED_ORDERS:
        block = by_order.get(order)
        if block is None:
            errors.append(f"missing producer-plan order {order}")
            continue
        plate_name = PLATE_BY_ORDER[order]
        plate = job / "generated_blocks" / plate_name
        if not plate.is_file():
            errors.append(f"missing source plate {plate}")
            continue
        cast_ids = CAST_BY_ORDER[order]
        cast_labels = [CAST_LABELS[cast_id] for cast_id in cast_ids]
        action = ACTION_BY_RECIPE[block["motion_recipe"]]
        prompt = (
            "Use the attached approved character references as internal production "
            "references only. Preserve their approved identities, "
            "face shapes, hair, clothing, palette, and props. Create a 10-second 16:9 original "
            "non-photorealistic woodblock-comic historical reconstruction based on the attached scene plate. "
            f"Narration beat for visual guidance only: {block['narration_excerpt']} "
            f"One clear action: {action} "
            "Use warm paper, indigo, rust, and jade with carved-line texture, a locked camera, and a restrained "
            f"{block['motion_recipe']} motion treatment. Keep the composition quiet and readable. "
            f"{NEGATIVE} Silent clip for narration, captions, citations, and credits added in post."
        )
        items.append(
            {
                "order": order,
                "block_id": block["block_id"],
                "coverage_slot_id": block["coverage_slot_id"],
                "narration_excerpt": block["narration_excerpt"],
                "semantic_purpose": block["semantic_purpose"],
                "motion_recipe": block["motion_recipe"],
                "duration_s": 10,
                "model_preference": "omni_flash",
                "settings": {"aspect_ratio": "16:9", "duration_s": 10, "variations": 1, "audio": "silent"},
                "character_ids": cast_ids,
                "character_labels": cast_labels,
                "source_plate": f"generated_blocks/{plate_name}",
                "source_plate_sha256": sha256(plate),
                "prompt": prompt,
                "status": "awaiting_flow_generation",
                "media_id": None,
                "output_path": f"flow-clips/{order:03d}.mp4",
                "render_eligible": False,
            }
        )

    if errors:
        raise SystemExit("\n".join(errors))
    payload = {
        "schema_version": "flow_clip_generation_queue.v1",
        "provider": "google_flow",
        "flow_project_url": "https://labs.google/fx/tools/flow/project/10984a51-81dd-49f9-928c-70ff31bb8751",
        "character_pack_id": "history-episode-1-flow-cast-v1",
        "source_plan": "character-motion-production/producer_plan.with-cast.json",
        "source_plan_hash": hashlib.sha256(plan_path.read_bytes()).hexdigest(),
        "count": len(items),
        "generation_policy": {
            "operator_submission_required": True,
            "paid_generation_completed": False,
            "render_eligible": False,
            "do_not_modify_gate_a": True,
            "narration_or_captions_in_post": True,
        },
        "items": items,
    }
    out = job / "character-motion-production/flow-17-generation-queue.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"path": str(out), "count": len(items), "errors": errors}, indent=2))


if __name__ == "__main__":
    main()
