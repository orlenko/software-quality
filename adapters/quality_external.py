"""Protocol2 thin entry for explicit external evidence. No policy or discovery."""
from pathlib import Path
import runpy
import sys

if not sys.flags.isolated or not sys.flags.no_site:
    raise SystemExit("use python3 -I -S adapters/quality_external.py")
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
runpy.run_path(str(root / "quality_external_launch.py"), run_name="__main__")
