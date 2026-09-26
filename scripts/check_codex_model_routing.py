"""Validate the operator's Codex model routing without starting model calls."""
from pathlib import Path
import sys
import tomllib


def check(root: Path) -> int:
    config = tomllib.loads((root / 'config.toml').read_text(encoding='utf-8-sig'))
    assert (config['model'], config['model_reasoning_effort']) == ('gpt-6-luna', 'max'), root
    sol_xhigh = {'architect_sol', 'execution_sol', 'professional_sol'}
    astra_high = {'execution_astra', 'professional_astra'}
    luna_max = {
        'speedster', 'junior_developer', 'implementation_luna',
        'release_steward', 'explorer', 'docs_researcher',
        'professional_worker', 'computer_use_worker',
    }
    expected_roles = sol_xhigh | astra_high | luna_max | {'reviewer'}
    count = 0
    for name, entry in config['agents'].items():
        if not isinstance(entry, dict):
            continue
        path = root / entry['config_file']
        role = tomllib.loads(path.read_text(encoding='utf-8-sig'))
        if name in sol_xhigh:
            expected = ('gpt-6-sol', 'xhigh')
        elif name == 'reviewer':
            expected = ('gpt-6-sol', 'high')
        elif name in astra_high:
            expected = ('gpt-6-astra', 'high')
        else:
            assert name in luna_max, name
            expected = ('gpt-6-luna', 'max')
        assert (role['model'], role['model_reasoning_effort']) == expected, path
        if name in luna_max:
            assert 'After 3 consecutive substantive task failures' in role['developer_instructions'], path
            assert 'Three consecutive failed tool calls trigger local inspection' in role['developer_instructions'], path
            assert 'including failed tool attempts' not in role['developer_instructions'], path
            assert 'gpt-6-sol at xhigh' in role['developer_instructions'], path
        if name in {'reviewer', 'explorer', 'docs_researcher'}:
            assert role['sandbox_mode'] == 'read-only', path
        count += 1
    assert set(config['agents']) - {'max_threads', 'max_depth'} == expected_roles, root
    assert count == len(expected_roles), (root, count)
    print(f'PASS: {count} registered roles, paths, models, efforts and escalation instructions: {root}')
    return count


if __name__ == '__main__':
    roots = [Path(p) for p in sys.argv[1:]] or [Path(__file__).resolve().parents[1] / '.codex']
    for root in roots:
        check(root)
