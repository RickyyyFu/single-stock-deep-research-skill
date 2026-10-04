import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.package_skill import archive_bytes, build, expected_members, source_files, verify_package
from scripts.validate_bundle import validate

class PackagingTests(unittest.TestCase):
    def test_bundle_validation(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertGreater(validate(), 20)

    def test_reproducible_bytes(self):
        self.assertEqual(archive_bytes(), archive_bytes())

    def test_archive_has_manifest_and_one_root(self):
        with ZipFile(io.BytesIO(archive_bytes())) as z:
            self.assertTrue(all(n.startswith('single-stock-deep-research/') for n in z.namelist()))
            m = json.loads(z.read('single-stock-deep-research/PACKAGE-MANIFEST.json'))
            self.assertEqual(m['version'], '3.5.0')
            self.assertIn('SKILL.md', m['files'])

    def test_no_old_zips_caches_or_live_data(self):
        for name in expected_members():
            self.assertNotIn('__pycache__', name)
            self.assertNotIn('/downloads/', name)
            self.assertNotIn('/outputs/', name)
            self.assertNotIn('.env', name)
            self.assertNotIn('MIGRATION-PROVENANCE', name)

    def test_allowlist_excludes_unlisted_private_file(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root/'bundle-files.json').write_text(json.dumps({'files':['bundle-files.json']}))
            (root/'private.json').write_text('private')
            self.assertNotIn('private.json', source_files(root))

    def test_allowlist_rejects_parent_traversal(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root/'bundle-files.json').write_text(json.dumps({'files':['bundle-files.json','../private']}))
            with self.assertRaisesRegex(ValueError, 'unsafe'):
                source_files(root)

    def test_package_rejects_changed_same_version(self):
        with tempfile.TemporaryDirectory() as td, contextlib.redirect_stdout(io.StringIO()):
            root = Path(td)
            for name, data in source_files().items():
                p = root/name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(data)
            build(root)
            (root/'ABOUT.md').write_text('changed without version increment')
            with self.assertRaisesRegex(ValueError, 'bump the version'):
                build(root)

    def test_check_does_not_create_missing_zip(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            shutil.copy(ROOT/'SKILL.md', root/'SKILL.md')
            with self.assertRaisesRegex(ValueError, 'missing'):
                build(root, check=True)
            self.assertFalse((root/'downloads').exists())

if __name__ == '__main__':
    unittest.main()
