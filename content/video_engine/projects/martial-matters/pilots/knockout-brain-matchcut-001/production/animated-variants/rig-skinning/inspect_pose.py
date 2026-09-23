"""Parent diagnostic renders from solved geometry; not final character art."""
from pathlib import Path
import sys
import cairosvg
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'rig-foundation'))
import rig_pose as r

ROOT=Path(__file__).resolve().parent


def main():
    for frame in (0,27,50,70,95):
        pose=r.evaluate_frame(frame/r.FPS)
        svg=['<svg xmlns="http://www.w3.org/2000/svg" width="700" height="960"><rect width="700" height="960" fill="#152235"/>',f'<path d="M 0 {r.FLOOR_Y} H 700" stroke="#ffffff"/>']
        for fighter,color in ((pose.victim,'#ae795c'),(pose.attacker,'#e3b88f')):
            coords=' '.join(f'{x},{y}' for x,y in fighter.torso)
            svg.append(f'<polygon points="{coords}" fill="{color}"/>')
            for chain in (*fighter.feet,fighter.arm('right'),fighter.arm('left')):
                coords=' '.join(f'{x},{y}' for x,y in (chain.root,chain.elbow,chain.end))
                svg.append(f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="35" stroke-linecap="round" stroke-linejoin="round"/>')
            svg.append(f'<circle cx="{fighter.head[0]}" cy="{fighter.head[1]}" r="{fighter.head_radius}" fill="{color}"/>')
            for side in ('right','left'):
                x,y=fighter.arm(side).end
                svg.append(f'<circle cx="{x}" cy="{y}" r="{r.GLOVE_RADIUS}" fill="#080c13"/>')
        svg.append('</svg>')
        cairosvg.svg2png(bytestring=''.join(svg).encode(),write_to=str(ROOT/f'pose-{frame}.png'))


if __name__=='__main__':
    main()
