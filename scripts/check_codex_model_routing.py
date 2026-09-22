"""Validate the operator's Codex model routing without starting model calls."""
from pathlib import Path
import sys
import tomllib


def check(root: Path) -> int:
    config = tomllib.loads((root / 'config.toml').read_text(encoding='utf-8-sig'))
    assert (config['model'], config['model_reasoning_effort']) == ('gpt-6-sol', 'xhigh'), root
    count = 0
    for name, entry in config['agents'].items():
        if not isinstance(entry, dict):
            continue
        path = root / entry['config_file']
        role = tomllib.loads(path.read_text(encoding='utf-8-sig'))
        sol = name in {'architect_sol', 'execution_sol', 'professional_sol'}
        expected = ('gpt-6-sol', 'xhigh') if sol else ('gpt-6-luna', 'max')
        assert (role['model'], role['model_reasoning_effort']) == expected, path
        if not sol:
            assert 'After 3 failures' in role['developer_instructions'], path
            assert 'gpt-6-sol at xhigh' in role['developer_instructions'], path
        if name in {'reviewer', 'explorer', 'docs_researcher'}:
            assert role['sandbox_mode'] == 'read-only', path
        count += 1
    assert count == 12, (root, count)
    print(f'PASS: {count} registered roles, paths, models, efforts and escalation instructions: {root}')
    return count


if __name__ == '__main__':
    roots = [Path(p) for p in sys.argv[1:]] or [Path(__file__).resolve().parents[1] / '.codex']
    for root in roots:
        check(root)
