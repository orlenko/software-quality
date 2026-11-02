"""Agent-neutral explicit adapter using the approved shared owned relay."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

if not sys.flags.isolated or not sys.flags.no_site:
    raise SystemExit("use an approved Python interpreter with -I -S")
HERE = Path(__file__).resolve().parent
if not (HERE / "quality_context.py").is_file():
    print("incomplete adapter resource closure", file=sys.stderr)
    raise SystemExit(2)
sys.path.insert(0, str(HERE))
try:
    from quality_context import launch, approved_path, outside_target
    from quality_trust import Cancellation, diagnostic, Invalid, selector_context
except ImportError:
    print("incomplete adapter resource closure", file=sys.stderr)
    raise SystemExit(2)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--launcher", type=Path, required=True, help="previously approved outside-target launcher")
    parser.add_argument("--python", type=Path, required=True, help="approved Python 3.11+ interpreter")
    parser.add_argument("arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if not args.arguments or args.arguments[0] not in {"doctor", "check"}:
        parser.error("adapter accepts doctor or check only")
    cancellation = Cancellation()
    with cancellation.handlers():
        try:
            repo, arguments = selector_context(args.arguments)
            assert repo is not None
            interpreter = approved_path(args.python, repo)
            launcher = outside_target(args.launcher, repo)
            if not launcher.is_file():
                raise Invalid("approved-launcher-unavailable")
            caller = Path.cwd()
        except (Invalid, OSError, ValueError, KeyboardInterrupt):
            diagnostic("incomplete: approved interpreter or launcher path unavailable", cancellation)
            return 2
        code, interrupted = launch([str(interpreter), "-I", "-S", str(launcher),
                                    "--adapter-protocol", "1", *arguments], cancellation,
                                   protected_roots=[repo], cwd=caller)
        if code == 1:
            return 1
        if interrupted or cancellation.requested:
            diagnostic("incomplete: owned adapter relay interrupted or cleanup unverified", cancellation)
            return 2
        return code


if __name__ == "__main__":
    raise SystemExit(main())
