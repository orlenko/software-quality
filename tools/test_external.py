"""Qualify source or an actual new import-only ZIP using invented records only."""
import argparse
from pathlib import Path
import sys
import unittest

if not sys.flags.isolated or not sys.flags.no_site:
    raise SystemExit("use python3 -I -S tools/test_external.py")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path)
    args = parser.parse_args()
    import tests.test_external as cases
    cases.ARTIFACT = args.artifact.resolve(strict=True) if args.artifact else None
    suite = unittest.defaultTestLoader.loadTestsFromModule(cases)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
