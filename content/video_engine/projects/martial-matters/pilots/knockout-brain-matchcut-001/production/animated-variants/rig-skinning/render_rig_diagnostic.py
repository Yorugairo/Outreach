"""Review-only rig animation: deliberately plain proxy geometry, not final art."""
from pathlib import Path
import math
import json
import subprocess
import sys
import cairosvg
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'rig-foundation'))
import rig_pose as r

ROOT=Path(__file__).resolve().parent


def circle(p,radius,color):
    return f'<circle cx="{p[0]}" cy="{p[1]}" r="{radius}" fill="{color}"/>'


def line(points,width,color):
    coords=' '.join(f'{x},{y}' for x,y in points)
    return f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>'


def svg_frame(pose):
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="540" height="960"><rect width="540" height="960" fill="#101925"/>',
         '<g fill="#c9d4de" font-family="Arial" text-anchor="middle"><text x="270" y="100" font-size="19">RIG / CONTACT TEST</text><text x="270" y="130" font-size="13">PROXY GEOMETRY — NOT CHARACTER ART</text></g>',
         '<g transform="translate(60,170) scale(.66)">',f'<path d="M -50 {r.FLOOR_Y} H 700" stroke="#677c90" stroke-width="3"/>']
    for fighter,color,shorts,wrap in ((pose.victim,'#a57157','#202a36','#eb6666'),(pose.attacker,'#dfb293','#f1eadb','#6a9fdf')):
        for foot in fighter.feet:
            svg.append(line((foot.root,foot.elbow,foot.end),36,color))
            svg.append(circle(foot.end,r.FOOT_RADIUS,color))
        coords=' '.join(f'{x},{y}' for x,y in fighter.torso)
        svg.append(f'<polygon points="{coords}" fill="{color}"/>')
        # Neck is a visible connection, not a floating head.
        chest=r.local_to_world(fighter.root,fighter.body_angle,(0,-170))
        svg.append(line((chest,fighter.head),34,color))
        hip=r.local_to_world(fighter.root,fighter.body_angle,(0,5))
        svg.append(f'<rect x="{hip[0]-51}" y="{hip[1]-28}" width="102" height="78" rx="12" fill="{shorts}" transform="rotate({math.degrees(fighter.body_angle)} {hip[0]} {hip[1]})"/>')
        svg.append(circle(fighter.head,fighter.head_radius,color))
        for side in ('left','right'):
            arm=fighter.arm(side)
            svg.append(line((arm.root,arm.elbow,arm.end),34,color))
            svg.append(circle(arm.end,r.GLOVE_RADIUS+3,wrap))
            svg.append(circle(arm.end,r.GLOVE_RADIUS-3,'#070e18'))
        # Simple eye marks only; deliberately not likeness art.
        svg.append(circle((fighter.head[0]-13,fighter.head[1]-5),3,'#1c1a1a'))
        svg.append(circle((fighter.head[0]+13,fighter.head[1]-5),3,'#1c1a1a'))
    if pose.brain is not None:
        for dx,dy,rad in ((-12,0,14),(4,-6,16),(15,7,12),(-5,12,13)):
            svg.append(circle((pose.brain[0]+dx,pose.brain[1]+dy),rad,'#edc762'))
    svg.append('</g></svg>')
    return ''.join(svg)


def main():
    frames=ROOT/'rig-diagnostic-frames'
    frames.mkdir(exist_ok=True)
    poses=r.evaluate_all_frames()
    measurements=[]
    for i,p in enumerate(poses):
        cairosvg.svg2png(bytestring=svg_frame(p).encode(),write_to=str(frames/f'{i:04}.png'))
        measurements.append(r.frame_measurement(p,poses[i-1] if i else None))
    (ROOT/'parent-rig-measurements.json').write_text(json.dumps(measurements,indent=2))
    video=ROOT/'rig-contact-diagnostic.mp4'
    subprocess.run(['ffmpeg','-y','-v','error','-framerate','24','-i',str(frames/'%04d.png'),'-c:v','libx264','-pix_fmt','yuv420p',str(video)],check=True)
    subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],check=True)
    print(json.dumps({'video':str(video),'frames':len(poses),'decode':'PASS','art_status':'diagnostic proxies only'}))


if __name__=='__main__':
    main()
