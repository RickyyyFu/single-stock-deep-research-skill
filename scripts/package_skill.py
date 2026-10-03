"""Build an immutable versioned skill ZIP. Run from any directory with Python 3."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import re

ROOT = Path(__file__).resolve().parents[1]


def build():
    text = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
    frontmatter = text.split('---', 2)[1]
    name = re.search(r'^name:\s*([a-z0-9-]+)\s*$', frontmatter, re.M).group(1)
    version = re.search(r'^\s+version:\s*"?(\d+\.\d+\.\d+)"?\s*$', frontmatter, re.M).group(1)
    files = [ROOT / item for item in ['SKILL.md', 'README.md', 'README.en.md', 'CHANGELOG.md', 'MIGRATION.md', 'VALIDATION.md', 'MIGRATION-PROVENANCE.json']]
    for folder in ['references', 'assets', 'scripts', 'tests']:
        files.extend(path for path in (ROOT / folder).rglob('*') if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc')
    expected = {f'{name}/{path.relative_to(ROOT).as_posix()}': path.read_bytes() for path in sorted(files)}
    destination = ROOT / 'downloads'
    destination.mkdir(exist_ok=True)
    output = destination / f'{name}-v{version}.zip'
    if output.exists():
        with ZipFile(output) as old:
            if old.testzip() is None and set(old.namelist()) == set(expected) and all(old.read(key) == value for key, value in expected.items()):
                print(f'{output.name}: unchanged, verified')
                return
        raise RuntimeError(f'{output.name} already exists with different content; bump the skill version before packaging')
    with ZipFile(output, 'w', ZIP_DEFLATED) as archive:
        for key, value in expected.items():
            archive.writestr(key, value)
    with ZipFile(output) as archive:
        assert archive.testzip() is None
        assert set(archive.namelist()) == set(expected)
        assert all(archive.read(key) == value for key, value in expected.items())
    print(f'{output.name}: verified {len(expected)} files')


if __name__ == '__main__':
    build()
