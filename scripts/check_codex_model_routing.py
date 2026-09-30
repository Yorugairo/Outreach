"""Validate Codex model routing and repair boundaries without model calls."""
import argparse
from pathlib import Path
import tomllib


def check(root: Path, scope: str = 'project') -> int:
    config = tomllib.loads((root / 'config.toml').read_text(encoding='utf-8-sig'))
    parent = ('gpt-6.1-sol', 'low') if scope == 'global' else ('gpt-6-luna', 'max')
    assert (config['model'], config['model_reasoning_effort']) == parent, root
    sol_xhigh = {'architect_sol', 'execution_sol', 'professional_sol'}
    sol_high = {'lead_developer', 'reviewer'}
    astra_high = {'execution_astra', 'professional_astra'} if scope == 'project' else set()
    luna_max = {
        'speedster', 'junior_developer', 'implementation_luna',
        'release_steward', 'explorer', 'docs_researcher',
        'professional_worker', 'computer_use_worker',
    }
    expected_roles = sol_xhigh | sol_high | astra_high | luna_max
    registered = set(config['agents']) - {'max_threads', 'max_depth'}
    assert registered == expected_roles, (root, registered, expected_roles)
    count = 0
    for name, entry in config['agents'].items():
        if name not in registered:
            continue
        assert isinstance(entry, dict), (root, name)
        assert isinstance(entry.get('config_file'), str) and entry['config_file'], (root, name)
        path = root / entry['config_file']
        role = tomllib.loads(path.read_text(encoding='utf-8-sig'))
        if name in sol_xhigh:
            expected = ('gpt-6.1-sol', 'xhigh')
        elif name in sol_high:
            expected = ('gpt-6.1-sol', 'high')
        elif name in astra_high:
            expected = ('gpt-6-astra', 'high')
        else:
            assert name in luna_max, name
            expected = ('gpt-6-luna', 'max')
        assert (role['model'], role['model_reasoning_effort']) == expected, path
        if name in luna_max and scope == 'project':
            assert 'After 3 consecutive substantive task failures' in role['developer_instructions'], path
            assert 'Three consecutive failed tool calls trigger local inspection' in role['developer_instructions'], path
            assert 'including failed tool attempts' not in role['developer_instructions'], path
            assert 'gpt-6.1-sol at xhigh' in role['developer_instructions'], path
        if name in {'explorer', 'docs_researcher'}:
            assert role['sandbox_mode'] == 'read-only', path
        if name in sol_high:
            assert role['sandbox_mode'] == 'workspace-write', path
            instructions = role['developer_instructions']
            assert 'Three consecutive failed tool calls trigger local' in instructions, path
        if name == 'reviewer':
            assert 'Explicit read-only orders remain read-only.' in instructions, path
            assert 'Do not approve your own repairs.' in instructions, path
            assert 'fresh independent review before integration' in instructions, path
            assert 'Never modify repository state.' not in instructions, path
        if name == 'lead_developer':
            assert 'No prior Luna failure requirement applies.' in instructions, path
            assert 'gpt-6.1-sol at xhigh diagnosis through execution_sol' in instructions, path
        if name == 'execution_sol':
            assert 'lead_developer at Sol high' in role['developer_instructions'], path
        count += 1
    assert count == len(expected_roles), (root, count)
    print(f'PASS: {scope}: {count} registered roles, paths, models, efforts, repair boundaries and escalation instructions: {root}')
    return count


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('roots', nargs='*', type=Path)
    parser.add_argument('--scope', choices=['project', 'global'], default='project')
    args = parser.parse_args()
    default = Path.home() / '.codex' if args.scope == 'global' else Path(__file__).resolve().parents[1] / '.codex'
    roots = args.roots or [default]
    for root in roots:
        check(root, args.scope)
