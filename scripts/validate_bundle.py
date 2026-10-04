"""Validate declared package files, local links, versions, and research contracts."""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path
try:
    from .package_skill import identity, source_files
    from .scenario_valuation import VERSION, evaluate
except ImportError:
    from package_skill import identity, source_files
    from scenario_valuation import VERSION, evaluate

ROOT = Path(__file__).resolve().parents[1]


def validate(root=ROOT):
    name, version = identity(root)
    files = source_files(root)
    required = {'SKILL.md', 'README.md', 'README.en.md', 'CHANGELOG.md', 'MIGRATION.md',
                'VALIDATION.md', 'ABOUT.md', 'references/11-scenario-valuation.md',
                'references/12-simulation-integration.md', 'references/13-prediction-evaluation.md',
                'assets/scenario-card.md', 'assets/scenario-example.json',
                'scripts/scenario_valuation.py', 'scripts/import_simulation.py'}
    if not required <= files.keys():
        raise ValueError(f'missing mandatory files: {sorted(required-files.keys())}')
    config = json.loads(files['assets/config.example.json'])
    if config['version'] != version or version != VERSION or config['skill_name'] != name:
        raise ValueError('entry point, configuration and calculator versions differ')
    if config['external_simulation']['enabled'] or config['external_simulation']['http_client_implemented']:
        raise ValueError('this release must not claim live MiroFish integration')
    for filename in ['README.md', 'README.en.md', 'CHANGELOG.md', 'MIGRATION.md', 'VALIDATION.md', 'ABOUT.md']:
        if version not in files[filename].decode('utf-8'):
            raise ValueError(f'missing current version in {filename}')
    for filename in ['README.md', 'README.en.md']:
        if f'downloads/{name}-v{version}.zip?raw=true' not in files[filename].decode('utf-8'):
            raise ValueError(f'incorrect current ZIP link in {filename}')
    text = '\n'.join(value.decode('utf-8') for key, value in files.items() if key.endswith('.md'))
    for word in ['Short Interest', 'Short Volume', '13F', 'GEX', 'Fuel', 'Trigger', 'Long unwind',
                 'two_sided_crowded', 'DMI', '+DI', '-DI', 'ADX上升不等于上涨', 'Model Conflict Review',
                 'DATED_SCENARIO', 'CURRENT_INTRINSIC', 'STRUCTURED_PERSPECTIVES', 'SIMULATION']:
        if word not in text:
            raise ValueError(f'missing research contract: {word}')
    # Only package-local Markdown links are checked. The two distribution links are repository-only by design.
    for filename, raw in files.items():
        if not filename.endswith('.md'):
            continue
        for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)', raw.decode('utf-8')):
            link = link.split('#')[0].split('?')[0]
            if not link or ':' in link or link.startswith('downloads/'):
                continue
            target = (root / filename).parent / link
            if not target.resolve().is_relative_to(root.resolve()) or not target.exists():
                raise ValueError(f'broken package link in {filename}: {link}')
    example = evaluate(json.loads(files['assets/scenario-example.json']))
    if example['input_mode'] != 'ILLUSTRATIVE' or any(r['status'] != 'ILLUSTRATIVE_NOT_FORECAST' for r in example['results']):
        raise ValueError('example must remain fictional and executable')
    print(f'bundle validation passed: {name} v{version}, {len(files)} allowlisted source files')
    return len(files)


if __name__ == '__main__':
    try:
        validate()
    except (ValueError, OSError, KeyError, IndexError, AttributeError) as exc:
        print(f'validation error: {exc}', file=sys.stderr)
        raise SystemExit(2)
