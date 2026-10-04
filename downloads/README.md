# Distribution files

## v3.5.0

Download the full versioned repository archive from the link in the root README. It includes the current SKILL.md, research rules, scripts and templates; use those directly rather than an older embedded ZIP.

The standalone v3.5.0 ZIP was built and tested separately; its SHA256 is recorded here. The ZIP binary has not been committed to this directory. Reproduce the exact standalone package with:

```sh
python -m unittest discover -s tests -v
python scripts/validate_bundle.py
python scripts/package_skill.py
python scripts/package_skill.py --check
```

The workflow can produce the standalone archive as an artifact when GitHub Actions is operational. Current remote attempts failed before executing any steps; do not infer a successful artifact upload from the workflow file alone.

Historical v3.4.0 and v3.4.1 ZIPs below are preserved byte-for-byte; they are not the current skill version.
