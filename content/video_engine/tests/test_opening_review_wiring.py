"""Human opening review is independent of the mechanical script verdict."""
import ast
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import opening_review as OR
import run_script_gates as RG

ROOT = Path(__file__).resolve().parents[3]


CALLER_FORMS = {
    'content/video_engine/scripts/record_short_take.py': '--short',
    'content/video_engine/scripts/record_master_take.py': '--long',
    'content/video_engine/scripts/record_chained_take.py': '--long',
}


def fixture(tmp_path):
    script = tmp_path / 'TEST-VO.txt'
    script.write_text('A bigger payment leaves less for wages. Stay for three checks and their public sources.', encoding='utf-8')
    RG.report_path(script).write_text(f'script_hash: {RG.script_hash(script.read_text())}\n[JUDGE] J13\n[JUDGE] J14\nVERDICT: PASS\n', encoding='utf-8')
    return script


def sidecar(script):
    return {'schema': OR.SCHEMA, 'script_hash': RG.script_hash(script.read_text()),
            'review_kind': 'estimated_draft', 'rows': [
        {'id': 'J13', 'verdict': 'PASS', 'quote': 'A bigger payment leaves less for wages.',
         'rationale': 'Payment competes with employee wages.', 'clock': 15, 'clock_basis': 'estimated'},
        {'id': 'J14', 'verdict': 'PASS', 'quote': 'Stay for three checks and their public sources.',
         'rationale': 'Names a repeatable test and its sources.', 'clock': 40, 'clock_basis': 'estimated'}]}


def test_recorders_forward_explicit_form_without_loading_credentials():
    """The shared preflight must never guess a recorder's short/long mode."""
    for relative, marker in CALLER_FORMS.items():
        tree = ast.parse((ROOT / relative).read_text(encoding='utf-8'))
        calls = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == 'recording_preflight'
        ]
        assert calls, relative
        for call in calls:
            literals = {node.value for node in ast.walk(call) if isinstance(node, ast.Constant)}
            assert marker in literals, (relative, ast.unparse(call))


def test_mechanical_pass_cannot_launder_missing_human_review(tmp_path):
    script = fixture(tmp_path)
    assert RG.check_report(script)[0] == 'incomplete'
    for argv in ([], ['--force', 'mechanical pass']):
        fails = []
        assert RG.recording_preflight(script, argv, fails) is None
        assert fails
    assert RG.opening_review_block(script, True)[0].startswith('OPENING REVIEW: FAIL')
    assert RG.recording_preflight(script, ['--force', 'diagnostic'], []) is None


def test_valid_human_draft_review_remains_partial_not_recording_clearance(tmp_path):
    script = fixture(tmp_path)
    OR.opening_review_path(script).write_text(json.dumps(sidecar(script)), encoding='utf-8')
    fails = []
    assert RG.recording_preflight(script, [], fails) is None
    assert fails
    assert not OR.validate_opening_review(script).recording_ready
    assert 'measured timing still required' in RG.opening_review_block(script, True)[0]


def test_legacy_short_report_still_needs_complete_recording_receipt(tmp_path):
    script = fixture(tmp_path)
    report = RG.report_path(script)
    report.write_text('form: short\n' + report.read_text().replace('J13', 'J50').replace('J14', 'J51'), encoding='utf-8')
    assert RG.recording_preflight(script, [], []) is None
    assert RG.opening_review_block(script, False) == []


def test_forced_unknown_report_cannot_bypass_opening_review(tmp_path):
    script = tmp_path / 'UNKNOWN-VO.txt'
    script.write_text('A consequence reaches a person. A useful check follows.', encoding='utf-8')
    fails = []
    assert RG.recording_preflight(script, ['--force', 'diagnostic'], fails) is None
    assert any('recording clearance missing' in failure for failure in fails)


def test_explicit_short_cannot_force_without_complete_receipt(tmp_path):
    script = tmp_path / 'SHORT-VO.txt'
    script.write_text('A short consequence and one useful check.', encoding='utf-8')
    fails = []
    assert RG.recording_preflight(script, ['--short', '--force', 'diagnostic'], fails) is None
    assert any('recording clearance missing' in failure for failure in fails)


def test_stale_short_metadata_does_not_authorize_force_without_explicit_short(tmp_path):
    script = tmp_path / 'STALE-VO.txt'
    script.write_text('A consequence reaches a person. A useful check follows.', encoding='utf-8')
    report = RG.report_path(script)
    report.write_text(
        'script_hash: ' + ('0' * 64) + '\nform: short\nVERDICT: PASS\n',
        encoding='utf-8',
    )
    fails = []
    assert RG.recording_preflight(script, ['--force', 'diagnostic'], fails) is None
    assert any('recording clearance stale' in failure for failure in fails)


def test_crashed_long_report_cannot_authorize_force(tmp_path):
    script = tmp_path / 'CRASHED-VO.txt'
    script.write_text('A consequence reaches a person. A useful check follows.', encoding='utf-8')
    RG.report_path(script).write_text(
        'script_hash: ' + RG.script_hash(script.read_text()) + '\n'
        'form: long\n## gate_opening_structure.py\nTraceback (most recent call last):\n'
        'VERDICT: FAIL (1 failing tools)\n',
        encoding='utf-8',
    )
    fails = []
    assert RG.recording_preflight(script, ['--force', 'diagnostic'], fails) is None
    assert any('recording clearance incomplete' in failure for failure in fails)
