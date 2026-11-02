"""Agent-neutral thin adapter; install outside the consumer checkout."""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

if not sys.flags.isolated or not sys.flags.no_site:
    raise SystemExit("use an approved Python interpreter with -I -S")
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--launcher", type=Path, required=True, help="previously approved outside-target launcher")
parser.add_argument("--python", type=Path, required=True, help="approved Python 3.11+ interpreter")
parser.add_argument("arguments", nargs=argparse.REMAINDER)
args = parser.parse_args()
if not args.arguments or args.arguments[0] not in {"doctor", "check"}:
    raise SystemExit("adapter accepts doctor or check only")
raise SystemExit(subprocess.call([str(args.python), "-I", "-S", str(args.launcher),
                                 "--adapter-protocol", "1", *args.arguments]))
