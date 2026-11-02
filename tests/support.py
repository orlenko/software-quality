"""Synthetic source/reviewer fixtures. These are not release provenance evidence."""
from __future__ import annotations

import io
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile
from typing import Any

import tests
from quality_trust import POLICY, PUBLISHER, VERSION, canonical, parse_json, sha

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "1" * 40
BOUNDARY = {"read_only": True, "enforced": True, "paths": "tracked-source",
            "tools": ["source-read", "diff-read"], "network": False, "disclosure": "none"}


def bundle(root: Path) -> tuple[Path, str, str]:
    if tests.ARTIFACT:
        data = tests.ARTIFACT.read_bytes()
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            source = parse_json(archive.read("manifest.json"))["source"]
    else:
        source = SOURCE
        payload = {"__main__.py": b"from quality.cli import main\nraise SystemExit(main())\n",
                   "quality_trust.py": (ROOT / "quality_trust.py").read_bytes()}
        for path in sorted((ROOT / "quality").rglob("*")):
            if path.is_file() and path.suffix in {".py", ".json"}:
                payload[path.relative_to(ROOT).as_posix()] = path.read_bytes()
        manifest = {"publisher": PUBLISHER, "version": VERSION, "source": source,
                    "policy_version": POLICY, "schema_version": 1,
                    "files": {key: sha(value) for key, value in payload.items()}}
        payload["manifest.json"] = canonical(manifest)
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as archive:
            for name, contents in sorted(payload.items()):
                archive.writestr(name, contents)
        data = buffer.getvalue()
    package = root / "fixture.pyz"
    package.write_bytes(data)
    return package, sha(data), source


class Fixture:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.repo = root / "target"
        self.repo.mkdir()
        self.state = root / "reports"
        self.cache = root / "cache"
        self.package, self.digest, self.source = bundle(root)
        self.git("init", "-q")
        self.git("config", "user.name", "Example Maintainer")
        self.git("config", "user.email", "maintainer@example.invalid")
        self.git("config", "core.hooksPath", os.devnull)
        self.config: dict[str, Any] = {
            "schema_version": 1, "repository": "example/demo",
            "execution": {"trusted_local": True, "isolation": "owner-approved-wrapper", "checks": [
                {"id": "unit", "argv": [sys.executable, "-I", "-S", "check.py"],
                 "timeout_seconds": 5, "max_log_bytes": 4096, "effects": ["disposable-files"]}]},
            "reviewer": {"protocol": "recorded-v1", "require_distinct_identities": True,
                         "routes": [{"id": "independent", "reviewer_id": "example-independent", "boundary": BOUNDARY}]},
            "references": {key: "instructions.md" for key in ("instructions", "architecture", "threat_model", "integration")}}
        self.lock = {"schema_version": 1, "publisher": PUBLISHER, "version": VERSION,
                     "source": self.source, "artifact_sha256": self.digest, "policy_version": POLICY}
        self.write("instructions.md", "Invented fixture; disposable files only.\n")
        self.write("check.py", "print('invented check')\n")
        self.accept()
        result = self.launch("install", "--artifact", str(self.package), "--sha256", self.digest,
                             "--source", self.source, "--cache", str(self.cache))
        if result.returncode:
            raise AssertionError(result.stderr)

    def git(self, *args: str) -> str:
        env = {"PATH": os.defpath + ":/opt/homebrew/bin", "HOME": str(self.root),
               "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
               "GIT_AUTHOR_DATE": "2001-01-01T00:00:00Z", "GIT_COMMITTER_DATE": "2001-01-01T00:00:00Z"}
        return subprocess.check_output(["git", "-c", "core.fsmonitor=false", "-C", str(self.repo), *args], env=env, stderr=subprocess.DEVNULL).decode().strip()

    def write(self, name: str, data: str) -> None:
        path = self.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data)

    def commit(self) -> str:
        self.git("add", ".")
        self.git("commit", "-qm", "Invented fixture change")
        return self.git("rev-parse", "HEAD")

    def accept(self) -> None:
        self.write(".quality/config.json", json.dumps(self.config))
        self.write(".quality/lock.json", json.dumps(self.lock))
        self.base = self.head = self.commit()

    def launch(self, *args: str, extra_env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        env = {"PATH": os.defpath, **(extra_env or {})}
        return subprocess.run([sys.executable, "-I", "-S", str(ROOT / "quality_launch.py"), *args],
                              env=env, capture_output=True, text=True, timeout=20)

    def command(self, mode: str = "check", *extra: str) -> list[str]:
        return [mode, "--repo", str(self.repo), "--base", self.base, "--head", self.head,
                "--identity", "example/demo", "--cache", str(self.cache), "--state", str(self.state), *extra]

    def check(self, *extra: str, mode: str = "check", extra_env: dict[str, str] | None = None) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
        result = self.launch(*self.command(mode, *extra), extra_env=extra_env)
        reports = sorted(self.state.glob("*/report.json"), key=lambda p: p.stat().st_mtime_ns)
        if not reports:
            raise AssertionError(result.stderr + result.stdout)
        return result, parse_json(reports[-1].read_bytes())

    def response(self, report: dict[str, Any], **updates: Any) -> tuple[str, str]:
        records = [{"route_id": route["id"], "reviewer_id": route["reviewer_id"], "independent": True,
                    "boundary": route["boundary"], "findings": [],
                    "summary": "Invented replay; no live reviewer accuracy claim."}
                   for route in self.config["reviewer"]["routes"]]
        value = {"schema_version": 1, "protocol": "recorded-v1", "context": report["context"], "reviews": records}
        value.update(updates)
        data = canonical(value)
        path = self.root / "review.json"
        path.write_bytes(data)
        return str(path), sha(data)

    def reviewed(self, *extra: str, **updates: Any) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
        _, initial = self.check(mode="doctor")
        path, digest = self.response(initial, **updates)
        return self.check("--execute-trusted", "--review", path, "--review-sha256", digest, *extra)
