"""Deterministic joint deformation comparison; authored weights, not BBW."""
from pathlib import Path
import math
import json
import subprocess
import cairosvg
from dqs import encode, apply, skin_mesh

ROOT = Path(__file__).resolve().parent


def area(a,b,c):
    return ((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))/2


def main():
    frames = ROOT/'joint-frames'
    frames.mkdir(exist_ok=True)
    nx, ny = 32, 6
    points = [(-1+2*x/nx, -.18+.36*y/ny) for y in range(ny+1) for x in range(nx+1)]
    weights = []
    for x,y in points:
        u = min(1.,max(0.,(x+.45)/.9))
        w = u*u*(3-2*u)
        weights.append({'upper':1-w,'lower':w})
    triangles = []
    for y in range(ny):
        for x in range(nx):
            a=y*(nx+1)+x
            triangles.extend(((a,a+1,a+nx+2),(a,a+nx+2,a+nx+1)))
    report=[]
    for frame in range(96):
        theta = math.radians(120)*math.sin(math.pi*frame/95)**2
        transforms = {'upper':encode(0,0,0),'lower':encode(0,0,theta)}
        dqs=skin_mesh(points,transforms,weights)
        lbs=[]
        for p,w in zip(points,weights):
            q=apply(transforms['lower'],p)
            lbs.append(tuple(p[i]*w['upper']+q[i]*w['lower'] for i in (0,1)))
        parts=['<svg xmlns="http://www.w3.org/2000/svg" width="960" height="540"><rect width="960" height="540" fill="#101925"/>',
               '<g fill="#f4eee0" font-family="Arial" text-anchor="middle"><text x="480" y="42" font-size="23">JOINT DEFORMATION • AUTHORED WEIGHTS</text><text x="240" y="91" font-size="18">LINEAR BLEND</text><text x="720" y="91" font-size="18">DUAL QUATERNION</text><text x="480" y="505" font-size="16">Actual mesh deformation · not a whole-mesh volume guarantee</text></g>']
        entry={'frame':frame,'angle_degrees':math.degrees(theta)}
        for label,mesh,cx,color in [('lbs',lbs,240,'#e4a269'),('dqs',dqs,720,'#69c4da')]:
            ratios=[]
            for tri in triangles:
                verts=[mesh[i] for i in tri]
                ratios.append(area(*verts)/area(*(points[i] for i in tri)))
                coords=' '.join(f'{cx+150*x:.3f},{330-150*y:.3f}' for x,y in verts)
                parts.append(f'<polygon points="{coords}" fill="{color}" stroke="#182b38" stroke-width=".65"/>')
            entry[label]={'min_signed_area_ratio':min(ratios),'inverted_triangles':sum(r<=0 for r in ratios)}
        report.append(entry)
        parts.append('</svg>')
        cairosvg.svg2png(bytestring=''.join(parts).encode(),write_to=str(frames/f'{frame:04}.png'))
    (ROOT/'joint-measurements.json').write_text(json.dumps(report,indent=2))
    subprocess.run(['ffmpeg','-y','-v','error','-framerate','24','-i',str(frames/'%04d.png'),'-c:v','libx264','-pix_fmt','yuv420p',str(ROOT/'joint-skinning-proof.mp4')],check=True)
    subprocess.run(['ffmpeg','-v','error','-i',str(ROOT/'joint-skinning-proof.mp4'),'-f','null','-'],check=True)
    print(json.dumps({'frames':96,'decode':'PASS','dqs_inverted_max':max(r['dqs']['inverted_triangles'] for r in report),'path':str(ROOT/'joint-skinning-proof.mp4')}))


if __name__=='__main__':
    main()
