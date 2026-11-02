"""Canonical deterministic checks: invented repositories, no external services."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import unittest

if not sys.flags.isolated or not sys.flags.no_site:
    raise SystemExit("use python3 -I -S tools/test.py")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, help="also exercise an externally built candidate")
    args = parser.parse_args()
    # Test-only binding; never consulted by production code.
    import tests
    tests.ARTIFACT = args.artifact.resolve(strict=True) if args.artifact else None
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), top_level_dir=str(ROOT))
    if suite.countTestCases() == 0:
        raise SystemExit("no tests found")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
