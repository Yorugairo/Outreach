"""Render hash-receipted, review-only planar contact frames 0/27/40/41.

The fixture and sidecar are diagnostic vectors. This probe makes no fighter-art,
skinning, impact-physics or production-render eligibility claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from content.video_engine.src.modeling.layered import DIAGNOSTIC_LABEL, LayeredScene  # noqa: E402


DEFAULT_SCENE = (ROOT / 'content/video_engine/tests/fixtures/modeling/layered/authored'
                 / 'knockout-authored-layers.v1.json')
DEFAULT_RIG = (ROOT / 'content/video_engine/tests/fixtures/modeling/layered/rig'
               / 'attacker-planted-foot.planar-rig.v1.json')
REVIEW_ROOT = ROOT / 'content/video_engine/review'
DEFAULT_OUT = REVIEW_ROOT / 'model-engines/benchmark-v1/2_5d/planar-rig'
FRAMES = (0, 27, 40, 41)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scene', type=Path, default=DEFAULT_SCENE)
    parser.add_argument('--rig', type=Path, default=DEFAULT_RIG)
    parser.add_argument('--out', type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    destination = args.out.resolve()
    if not destination.is_relative_to(REVIEW_ROOT.resolve()):
        parser.error('--out must remain inside content/video_engine/review quarantine')
    scene = LayeredScene.load(args.scene, planar_rig_path=args.rig)
    destination.mkdir(parents=True, exist_ok=True)
    try:
        font = ImageFont.truetype('arial.ttf', 18)
    except OSError:
        font = ImageFont.load_default()
    measure = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    banner_lines: list[str] = []
    for word in DIAGNOSTIC_LABEL.split():
        candidate = f'{banner_lines[-1]} {word}' if banner_lines else word
        if banner_lines and measure.textlength(candidate, font=font) > scene.width * 2 - 24:
            banner_lines.append(word)
        elif banner_lines:
            banner_lines[-1] = candidate
        else:
            banner_lines.append(word)
    banner_height = max(56, len(banner_lines) * 24 + 12)
    sheet = Image.new('RGB', (scene.width * 2, banner_height + 2 * (scene.height + 32)), (16, 18, 24))
    draw = ImageDraw.Draw(sheet)
    for index, line in enumerate(banner_lines):
        draw.text((12, 8 + index * 24), line, font=font, fill=(255, 208, 77))
    records = []
    for index, frame in enumerate(FRAMES):
        render = scene.render(frame)
        pose = render.state.planar_pose
        assert pose is not None
        image_path = destination / f'frame-{frame:03}.png'
        render.image.save(image_path, format='PNG', optimize=True)
        x = (index % 2) * scene.width
        y = banner_height + (index // 2) * (scene.height + 32)
        sheet.paste(render.image, (x, y))
        draw.text((x + 8, y + scene.height + 4),
                  f'frame {frame}: {pose.mode}, residual {pose.residual_px:.4f}px',
                  font=font, fill=(235, 239, 246))
        records.append({
            'frame': frame,
            'image': image_path.name,
            'sha256': _sha256(image_path),
            'events': list(render.state.events),
            'contacts': list(render.state.contacts),
            'pose': asdict(pose),
        })
    sheet_path = destination / 'contact-sheet.png'
    sheet.save(sheet_path, format='PNG', optimize=True)
    receipt = {
        'schema_version': 'planar_rig_probe_receipt.v1',
        'review_state': 'review_only',
        'render_eligible': False,
        'diagnostic_only': True,
        'scene_id': scene.scene_id,
        'diagnostic_label': DIAGNOSTIC_LABEL,
        'scene_source': str(args.scene.resolve().relative_to(ROOT)),
        'scene_sha256': _sha256(args.scene),
        'rig_source': str(args.rig.resolve().relative_to(ROOT)),
        'rig_sha256': _sha256(args.rig),
        'implementation_sha256': {
            'planar_rig.py': _sha256(ROOT / 'content/video_engine/src/modeling/planar_rig.py'),
            'layered.py': _sha256(ROOT / 'content/video_engine/src/modeling/layered.py'),
            'model_planar_rig_probe.py': _sha256(Path(__file__)),
        },
        'shared_contact_id': scene.planar_rig.contact.contact_id if scene.planar_rig else None,
        'frames': records,
        'contact_sheet': {'path': sheet_path.name, 'sha256': _sha256(sheet_path),
                          'canvas_px': list(sheet.size)},
        'limits': [
            'Diagnostic vector art; no real-person likeness or approved fighter art.',
            'Numerical reach and a visible foot marker do not certify skinning, impact force, or finished animation.',
            'All timing comes from the shared MotionTimeline contact interval.',
        ],
    }
    receipt_path = destination / 'receipt.json'
    receipt_path.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'sheet': str(sheet_path), 'sheet_sha256': _sha256(sheet_path),
                      'receipt': str(receipt_path), 'frames': list(FRAMES)}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
