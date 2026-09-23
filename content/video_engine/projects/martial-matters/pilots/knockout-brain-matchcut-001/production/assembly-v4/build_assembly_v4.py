"""Isolated head-snap revision using the existing scene-evidence compiler."""
from pathlib import Path
import importlib.util
import json

HERE=Path(__file__).resolve().parent
PROD=HERE.parent
spec=importlib.util.spec_from_file_location('v2_adapter',PROD/'assembly-v2/build_assembly_v2.py')
v2=importlib.util.module_from_spec(spec); spec.loader.exec_module(v2)
v2.HERE=HERE
v2.EPISODE_ID='knockout-brain-matchcut-001-v4'
v2.TIMELINE_NAME=v2.EPISODE_ID+'.timeline.json'
v2.OUTPUT_NAME=v2.EPISODE_ID+'.mp4'
v2.SHOT_TABLE_RELATIVE='production/assembly-v4/SHOT-TABLE.py'
v2.BASE.BUILD=HERE/'build'
v2.BASE.SHOT_TABLE=HERE/'SHOT-TABLE.py'
v2.BASE.EPISODE_ID=v2.EPISODE_ID
v2.BASE.TIMELINE_NAME=v2.TIMELINE_NAME
v2.BASE.DEFAULT_EDIT=PROD/'edit-v4.json'
v2.BASE.DEFAULT_AUDIO=PROD/'audio/master-v4.wav'
v2.BASE.__doc__=__doc__
previous=v2.BASE._write_timeline_inputs
def inputs(*args):
    previous(*args)
    path=v2.BASE.BUILD/'timeline.json'
    payload=json.loads(path.read_text(encoding='utf-8')); payload['script']='production/edit-v4.json'
    path.write_text(json.dumps(payload,indent=1),encoding='utf-8')
v2.BASE._write_timeline_inputs=inputs
if __name__=='__main__':
    raise SystemExit(v2.main())
