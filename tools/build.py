"""Build a deterministic, unpublished ZIP application from a clean source commit."""
from __future__ import annotations

import argparse
import io
import os
from pathlib import Path
import sys
import zipfile

if not sys.flags.isolated or not sys.flags.no_site:
    raise SystemExit("use python3 -I -S tools/build.py")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from quality_trust import Git, Invalid, POLICY, PUBLISHER, VERSION, canonical, sha


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    git = Git(ROOT)
    state = git.state()
    if state["status_sha256"] != sha(b""):
        raise Invalid("clean-source-required")
    source = git.commit(state["head"])
    names = git.run("ls-tree", "-r", "--name-only", source).decode().splitlines()
    payload: dict[str, bytes] = {
        "__main__.py": b"from quality.cli import main\nraise SystemExit(main())\n",
        "quality_trust.py": git.blob(source, "quality_trust.py"),
        "policy/development-standard.md": git.blob(source, "docs/development-standard.md"),
        "policy/toolkit-design.md": git.blob(source, "docs/toolkit-design.md"),
        "policy/LICENSE": git.blob(source, "LICENSE"),
    }
    for name in names:
        if name.startswith("quality/") and (name.endswith(".py") or name.endswith(".json")):
            payload[name] = git.blob(source, name)
    manifest = {"publisher": PUBLISHER, "version": VERSION, "source": source,
                "policy_version": POLICY, "schema_version": 1,
                "files": {name: sha(data) for name, data in payload.items()}}
    payload["manifest.json"] = canonical(manifest)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, data in sorted(payload.items()):
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    data = buffer.getvalue()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(args.output, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as output:
        output.write(data)
    print(canonical({"version": VERSION, "source": source, "artifact_sha256": sha(data)}).decode(), end="")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Invalid, OSError, ValueError):
        raise SystemExit("build refused: check clean source and output path")
