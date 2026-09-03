from pathlib import Path
from PIL import Image
import hashlib, json, shutil

root = Path(__file__).parent
srcs = {
    'host-board-present-v1': Path(r'C:\Users\Snipe\.codex\generated_images\01a06635-4621-7ee1-9e09-749ecfe762cc\exec-c767cd23-3d91-4d78-b8e3-98549f34addb.png'),
    'host-board-point-v1': Path(r'C:\Users\Snipe\.codex\generated_images\01a06635-4621-7ee1-9e09-749ecfe762cc\exec-c31ae7af-253a-4919-b7ac-f4d78322be81.png'),
    'host-board-turned-v1': Path(r'C:\Users\Snipe\.codex\generated_images\01a06635-4621-7ee1-9e09-749ecfe762cc\exec-3cfb3ef7-4943-45d7-ae6a-a4e757087fa4.png'),
}
(root/'source').mkdir(exist_ok=True); (root/'objects').mkdir(exist_ok=True)
for aid, src in srcs.items():
    im = Image.open(src).convert('RGB').resize((1920,1080), Image.Resampling.LANCZOS)
    for folder, name in [('source', f'{aid}-source.png'), ('objects', f'{aid}.png')]:
        im.save(root/folder/name, format='PNG')
    print(aid, im.size, im.mode)

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
assets=[]
for aid in srcs:
    obj=root/'objects'/f'{aid}.png'; source=root/'source'/f'{aid}-source.png'
    assets.append({'asset_id':aid,'path':f'objects/{obj.name}','sha256':sha(obj),'kind':'world_board','semantic':'','source':{'path':f'source/{source.name}','sha256':sha(source)}})
(root/'steel-and-paper-host-board-v1.manifest.json').write_text(json.dumps({'schema_version':'review_manifest.v1','status':'review_only','render_eligible':False,'style_family':'woodblock-vox-newsprint-v2','source_prompt':'claim:steel-and-paper-host-board-v1','assets':assets},indent=2)+'\n')
