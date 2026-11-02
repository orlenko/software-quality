"""Canonical deterministic checks: invented repositories, no external services."""
from __future__ import annotations

import argparse
import re
from pathlib import Path
import sys
import tempfile
import zipfile
import unittest

if not sys.flags.isolated or not sys.flags.no_site:
    raise SystemExit("use python3 -I -S tools/test.py")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, help="also exercise an externally built candidate")
    parser.add_argument("--adapter-bundle", type=Path, help="exercise a locally built adapter/skill bundle")
    parser.add_argument("--match", help="run only test IDs matching this regular expression")
    args = parser.parse_args()
    # Test-only binding; never consulted by production code.
    import tests
    tests.ARTIFACT = args.artifact.resolve(strict=True) if args.artifact else None
    bundle_directory = tempfile.TemporaryDirectory()
    if args.adapter_bundle:
        from quality_trust import parse_json, sha
        with zipfile.ZipFile(args.adapter_bundle) as archive:
            manifest = parse_json(archive.read("bundle.json"))
            if set(archive.namelist()) != set(manifest["files"]) | {"bundle.json"}:
                raise SystemExit("invalid owned bundle inventory")
            for name, digest in manifest["files"].items():
                if Path(name).is_absolute() or ".." in Path(name).parts or "\\" in name:
                    raise SystemExit("invalid owned bundle member")
                data = archive.read(name)
                if sha(data) != digest:
                    raise SystemExit("invalid owned bundle digest")
                path = Path(bundle_directory.name) / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
        tests.ADAPTER_ROOT = Path(bundle_directory.name)
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), top_level_dir=str(ROOT))
    if args.match:
        pattern = re.compile(args.match)
        def selected(items):
            for item in items:
                if isinstance(item, unittest.TestSuite):
                    yield from selected(item)
                elif pattern.search(item.id()):
                    yield item
        suite = unittest.TestSuite(selected(suite))
    if suite.countTestCases() == 0:
        raise SystemExit("no tests found")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    bundle_directory.cleanup()
    raise SystemExit(0 if result.wasSuccessful() else 1)
