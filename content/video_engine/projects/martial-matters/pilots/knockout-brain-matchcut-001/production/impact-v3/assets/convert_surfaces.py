"""Convert Nilearn's bundled anatomical GIFTI surfaces into a combined OBJ."""
from pathlib import Path
import gzip
import base64
import zlib
import xml.etree.ElementTree as ET
import numpy as np
import json
import hashlib

HERE = Path(__file__).resolve().parent
lines = ['# FreeSurfer fsaverage5 pial cortical surfaces, distributed by Nilearn']
offset = 0
record = []
for side in ['left', 'right']:
    path = HERE / f'pial_{side}.gii.gz'
    root = ET.fromstring(gzip.decompress(path.read_bytes()))
    arrays = {}
    for node in root.findall('DataArray'):
        dtype = '<f4' if node.attrib['DataType'] == 'NIFTI_TYPE_FLOAT32' else '<i4'
        raw = zlib.decompress(base64.b64decode(node.findtext('Data')))
        values = np.frombuffer(raw, dtype=dtype).reshape(int(node.attrib['Dim0']), 3)
        arrays[node.attrib['Intent']] = values
    vertices = arrays['NIFTI_INTENT_POINTSET']
    faces = arrays['NIFTI_INTENT_TRIANGLE']
    lines.append(f'o cortex_{side}')
    lines.extend('v %.7f %.7f %.7f' % tuple(v) for v in vertices)
    lines.extend('f %d %d %d' % tuple(f+offset+1) for f in faces)
    record.append({'hemisphere': side, 'vertices': len(vertices), 'triangles': len(faces),
                   'bounds': [vertices.min(axis=0).tolist(), vertices.max(axis=0).tolist()],
                   'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    offset += len(vertices)
(HERE/'brain.obj').write_text('\n'.join(lines)+'\n', encoding='utf-8')
(HERE/'surface-record.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
print(json.dumps(record, indent=2))
