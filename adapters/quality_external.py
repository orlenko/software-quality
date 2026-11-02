"""Protocol2 thin entry for explicit external evidence. No policy or discovery."""
from pathlib import Path
import runpy
import sys

if not sys.flags.isolated or not sys.flags.no_site:
    raise SystemExit("use python3 -I -S adapters/quality_external.py")
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
from quality_trust import Invalid, outside_path, selector_context

try:
    repo, arguments = selector_context(sys.argv[1:], subjectless_install=True)
    roots = [repo] if repo else []
    entry = outside_path(Path(sys.argv[0]), roots, strict=True)
    bootstrap = outside_path(entry.parent.parent / "quality_external_launch.py", roots, strict=True)
except (Invalid, OSError, ValueError):
    print("incomplete: explicit outside-target bootstrap context required", file=sys.stderr)
    raise SystemExit(2)
sys.argv = [str(bootstrap), *arguments]
runpy.run_path(str(bootstrap), run_name="__main__")
