"""Actual ffmpeg regression: a voice-only mix must not begin with an empty filter."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import render_episode as RE


@pytest.mark.skipif(not shutil.which('ffmpeg') or not shutil.which('ffprobe'), reason='ffmpeg required')
@pytest.mark.parametrize('with_cue', [False, True])
def test_real_voice_mix_with_and_without_cues(tmp_path, monkeypatch, with_cue):
    build = tmp_path / 'build'
    (build / 'audio').mkdir(parents=True)
    (build / 'timeline.json').write_text('{}', encoding='utf-8')
    voice = build / 'audio/episode.mp3'
    subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i',
                    'sine=frequency=440:duration=0.5', '-y', str(voice)], check=True)
    if with_cue:
        sound = tmp_path / 'sound'
        sound.mkdir()
        shutil.copyfile(voice, sound / 'cue.mp3')
        (sound / 'SOUND-PLAN.json').write_text(json.dumps({'cues': [{
            'variants': {'A': 'cue.mp3'}, 'gain': 0.1, 'at': 0,
            'fade_in': 0.05, 'env': [[0, -4], [0.4, 0]],
        }]}), encoding='utf-8')
    monkeypatch.setattr(RE, 'BUILD', build)
    monkeypatch.setattr(RE, 'OUT', build / 'render')
    result = RE.mix_audio(0.5)
    probe = subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                            'format=duration:stream=codec_name,sample_rate', '-of', 'json', str(result)],
                           check=True, capture_output=True, text=True)
    data = json.loads(probe.stdout)
    assert result.stat().st_size > 1000
    assert data['streams'][0]['codec_name'] == 'aac'
    assert data['streams'][0]['sample_rate'] == '48000'
    assert abs(float(data['format']['duration']) - 0.5) < 0.05
