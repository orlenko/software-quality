"""Deterministic unpublished engine0.2 import-only ZIP. No execution modules."""
from __future__ import annotations

import argparse
import io
import os
from pathlib import Path
import sys
import zipfile
from typing import Callable

if not sys.flags.isolated or not sys.flags.no_site:
    raise SystemExit("use python3 -I -S tools/build_external.py")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from quality_trust import EXTERNAL_VERSION, Git, Invalid, POLICY, PUBLISHER, canonical, sha

MODULES = ("__init__", "schema", "evidence", "external_clock", "external_model", "external_store", "external_cli")
SCHEMAS = ("common", "config", "record", "envelope", "observer", "report", "state")


def payload(read: Callable[[str], bytes]) -> dict[str, bytes]:
    # read is a caller-owned byte reader, never a target import or producer.
    result = {"__main__.py": b"from quality.external_cli import main\nraise SystemExit(main())\n",
              "quality_trust.py": read("quality_trust.py"),
              "policy/development-standard.md": read("docs/development-standard.md"),
              "policy/toolkit-design.md": read("docs/toolkit-design.md"), "policy/LICENSE": read("LICENSE")}
    result.update({"quality/" + name + ".py": read("quality/" + name + ".py") for name in MODULES})
    result.update({"quality/schemas/external-" + name + ".json": read("quality/schemas/external-" + name + ".json") for name in SCHEMAS})
    return result


def archive(files: dict[str, bytes], source: str) -> bytes:
    files = dict(files)
    files["manifest.json"] = canonical({"publisher": PUBLISHER, "version": EXTERNAL_VERSION, "source": source,
        "policy_version": POLICY, "schema_version": 2, "files": {name: sha(data) for name, data in files.items()}})
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as package:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            package.writestr(info, data)
    return buffer.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    git = Git(ROOT)
    state = git.state()
    if state["status_sha256"] != sha(b""):
        raise Invalid("clean-source-required")
    source = git.commit(state["head"])
    data = archive(payload(lambda name: git.blob(source, name)), source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(args.output, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
    print(canonical({"version": EXTERNAL_VERSION, "source": source, "artifact_sha256": sha(data)}).decode(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
