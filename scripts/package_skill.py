"""Build or verify an immutable, allowlisted, reproducible standalone skill ZIP."""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import re
from pathlib import Path, PurePosixPath
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]


def identity(root=ROOT):
    text = (root / 'SKILL.md').read_text(encoding='utf-8')
    frontmatter = text.split('---', 2)[1]
    name = re.search(r'^name:\s*([a-z0-9-]+)\s*$', frontmatter, re.M).group(1)
    version = re.search(r'^\s+version:\s*"?(\d+\.\d+\.\d+)"?\s*$', frontmatter, re.M).group(1)
    return name, version


def source_files(root=ROOT):
    config = json.loads((root / 'bundle-files.json').read_text(encoding='utf-8'))
    names = config['files']
    if not isinstance(names, list) or len(names) != len(set(names)) or 'bundle-files.json' not in names:
        raise ValueError('invalid or duplicate package allowlist')
    result = {}
    for name in sorted(names):
        if not isinstance(name, str):
            raise ValueError('package paths must be strings')
        rel = PurePosixPath(name)
        if rel.is_absolute() or '..' in rel.parts or '\\' in name or rel.as_posix() != name:
            raise ValueError(f'unsafe package path: {name}')
        path = root / name
        if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()) or not path.is_file():
            raise ValueError(f'missing, escaping or symbolic-link package entry: {name}')
        if any(part in {'.git', '__pycache__', 'downloads', 'outputs', '.env'} for part in rel.parts):
            raise ValueError(f'disallowed package path: {name}')
        result[name] = path.read_bytes()
    return result


def expected_members(root=ROOT):
    name, version = identity(root)
    files = source_files(root)
    manifest = {'skill_name': name, 'version': version, 'algorithm': 'sha256',
                'files': {key: hashlib.sha256(value).hexdigest() for key, value in files.items()}}
    files['PACKAGE-MANIFEST.json'] = (json.dumps(manifest, ensure_ascii=False, indent=2)+'\n').encode('utf-8')
    return {f'{name}/{key}': value for key, value in files.items()}


def archive_bytes(root=ROOT):
    stream = io.BytesIO()
    with ZipFile(stream, 'w', compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for name, content in sorted(expected_members(root).items()):
            info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content, compresslevel=9)
    return stream.getvalue()


def verify_package(path, root=ROOT):
    expected = expected_members(root)
    with ZipFile(path) as archive:
        if archive.testzip() is not None or len(archive.namelist()) != len(expected) or set(archive.namelist()) != set(expected):
            raise ValueError('archive member list or CRC mismatch')
        for name, data in expected.items():
            if archive.read(name) != data:
                raise ValueError(f'archive source mismatch: {name}')
    return len(expected)


def build(root=ROOT, check=False):
    name, version = identity(root)
    destination = root / 'downloads' / f'{name}-v{version}.zip'
    checksum = destination.with_suffix('.zip.sha256')
    if destination.exists():
        try:
            count = verify_package(destination, root)
        except (ValueError, OSError) as exc:
            raise ValueError('existing version has different contents; bump the version, never overwrite a published ZIP') from exc
        if destination.read_bytes() != archive_bytes(root):
            raise ValueError('archive is not reproducible from the declared source')
    else:
        if check:
            raise ValueError('versioned ZIP is missing')
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open('xb') as handle:
            handle.write(archive_bytes(root))
        count = verify_package(destination, root)
    digest = hashlib.sha256(destination.read_bytes()).hexdigest()
    line = f'{digest}  {destination.name}\n'
    if checksum.exists():
        if checksum.read_text(encoding='utf-8') != line:
            raise ValueError('ZIP checksum file mismatch')
    elif check:
        raise ValueError('ZIP checksum file is missing')
    else:
        with checksum.open('x', encoding='utf-8') as handle:
            handle.write(line)
    print(f'{destination.name}: verified {count} files; SHA256 {digest}')
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='verify only; do not create files')
    args = parser.parse_args()
    try:
        build(check=args.check)
    except (ValueError, OSError, KeyError, IndexError, AttributeError) as exc:
        parser.exit(2, f'package error: {exc}\n')


if __name__ == '__main__':
    main()
