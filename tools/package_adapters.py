"""Build a deterministic source/skill bundle; no installation or host registration."""
from __future__ import annotations

import argparse
import io
import os
from pathlib import Path
import sys
import zipfile

if not sys.flags.isolated or not sys.flags.no_site:
    raise SystemExit("use python3 -I -S tools/package_adapters.py")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from quality_trust import Git, Invalid, canonical, parse_json, sha


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    git = Git(ROOT)
    state = git.state()
    if state["status_sha256"] != sha(b""):
        raise Invalid("clean-adapter-source-required")
    source = git.commit(state["head"])
    mapping = {"bin/quality_context.py": "adapters/quality_context.py",
               "bin/quality.py": "adapters/quality.py", "bin/quality_trust.py": "quality_trust.py",
               "bin/quality/__init__.py": "quality/__init__.py", "bin/quality/process.py": "quality/process.py",
               "workflow.md": "adapters/workflow.md", "compatibility.json": "adapters/compatibility.json",
               "LICENSE": "LICENSE"}
    for path in git.run("ls-tree", "-r", "--name-only", source, "adapters/skills").decode().splitlines():
        mapping[path.removeprefix("adapters/")] = path
    payload = {name: git.blob(source, original) for name, original in mapping.items()}
    compatibility = parse_json(payload["compatibility.json"])
    payload["bundle.json"] = canonical({"source": source, "adapter_version": compatibility["adapter_version"],
        "adapter_protocol": compatibility["adapter_protocol"], "files": {name: sha(data) for name, data in payload.items()}})
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, data in sorted(payload.items()):
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    data = buffer.getvalue()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as output:
        output.write(data)
    print(canonical({"source": source, "adapter_protocol": 1, "bundle_sha256": sha(data)}).decode(), end="")


if __name__ == "__main__":
    try:
        main()
    except (Invalid, OSError, ValueError):
        raise SystemExit("bundle refused: check clean source and output")
