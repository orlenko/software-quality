"""Trusted bootstrap primitives. No target imports, network or policy execution."""
from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import zipfile
from typing import Any

VERSION = "0.1.0"
EXTERNAL_VERSION = "0.2.0"
POLICY = "0.1"
PUBLISHER = "orlenko/software-quality"
MAX_JSON = 2 * 1024 * 1024
MAX_ARTIFACT = 32 * 1024 * 1024
OID = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
DIGEST = re.compile(r"[0-9a-f]{64}\Z")
SAFE_PATH = os.defpath + ":/opt/homebrew/bin:/usr/local/bin"


class Invalid(ValueError):
    """A stable diagnostic code; never includes private input."""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def parse_json(data: bytes) -> Any:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise Invalid("duplicate-json-key")
            result[key] = value
        return result

    if len(data) > MAX_JSON:
        raise Invalid("json-too-large")
    try:
        return json.loads(data, object_pairs_hook=pairs, parse_constant=lambda _: (_ for _ in ()).throw(Invalid("nonfinite-json")))
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise Invalid("invalid-json") from exc


def object_keys(value: Any, keys: set[str]) -> dict[str, Any]:
    if type(value) is not dict or set(value) != keys:
        raise Invalid("invalid-object-fields")
    return value


def lock_value(data: bytes, *, version: str = VERSION, schema_version: int = 1) -> dict[str, Any]:
    value = object_keys(parse_json(data), {"schema_version", "publisher", "source", "artifact_sha256", "version", "policy_version"})
    if (type(value["schema_version"]) is not int or value["schema_version"] != schema_version
            or value["publisher"] != PUBLISHER or value["version"] != version
            or value["policy_version"] != POLICY
            or not isinstance(value["source"], str) or not OID.fullmatch(value["source"])
            or not isinstance(value["artifact_sha256"], str) or not DIGEST.fullmatch(value["artifact_sha256"])):
        raise Invalid("unsupported-or-invalid-lock")
    return value


def regular_bytes(path: Path, limit: int) -> bytes:
    """Open once without following a final symlink; bound and read the same bytes."""
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > limit:
            raise Invalid("invalid-input-file")
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise Invalid("input-too-large")
    return data


def within(path: Path, root: Path) -> bool:
    return path.resolve().is_relative_to(root.resolve())


def outside_path(path: Path, roots: list[Path]) -> Path:
    """Reject paths traversing a protected ancestor, even if a later link exits it."""
    if ".." in path.parts:
        raise Invalid("parent-path-components-unsupported")
    lexical = Path(os.path.abspath(path))
    for candidate in (lexical, *lexical.parents):
        if any(candidate.resolve().is_relative_to(root.resolve()) for root in roots):
            raise Invalid("path-traverses-protected-root")
    return path.resolve()


def artifact(data: bytes, digest: str, source: str, *, version: str = VERSION,
             schema_version: int = 1, entrypoint: str = "quality/cli.py") -> dict[str, Any]:
    if not DIGEST.fullmatch(digest) or not OID.fullmatch(source) or sha(data) != digest:
        raise Invalid("artifact-identity-mismatch")
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            infos = archive.infolist()
            names = [item.filename for item in infos]
            if len(names) != len(set(names)) or len(names) > 100:
                raise Invalid("invalid-artifact-members")
            for info in infos:
                name = info.filename
                parts = PurePosixPath(name).parts
                if (not parts or name.startswith("/") or ".." in parts or "\\" in name
                        or info.is_dir() or stat.S_ISLNK(info.external_attr >> 16)
                        or info.file_size > MAX_ARTIFACT):
                    raise Invalid("invalid-artifact-member")
            if sum(info.file_size for info in infos) > MAX_ARTIFACT:
                raise Invalid("artifact-too-large")
            manifest = object_keys(parse_json(archive.read("manifest.json")),
                                   {"publisher", "version", "source", "policy_version", "schema_version", "files"})
            expected = {"publisher": PUBLISHER, "version": version, "source": source,
                        "policy_version": POLICY, "schema_version": schema_version}
            if any(type(manifest[key]) is not type(value) or manifest[key] != value for key, value in expected.items()):
                raise Invalid("artifact-manifest-mismatch")
            files = manifest["files"]
            if type(files) is not dict or set(names) != set(files) | {"manifest.json"}:
                raise Invalid("artifact-inventory-mismatch")
            if not {"__main__.py", "quality_trust.py", "quality/__init__.py", entrypoint} <= set(files):
                raise Invalid("artifact-entrypoint-missing")
            for name, expected_sha in files.items():
                if not isinstance(expected_sha, str) or sha(archive.read(name)) != expected_sha:
                    raise Invalid("artifact-member-mismatch")
            return manifest
    except (zipfile.BadZipFile, KeyError, RuntimeError, NotImplementedError) as exc:
        raise Invalid("invalid-artifact") from exc


class Git:
    """Inspection only: fixed Git executable and no inherited Git authority."""

    def __init__(self, repo: Path) -> None:
        self.repo = repo.resolve(strict=True)
        executable = shutil.which("git", path=SAFE_PATH)
        if executable is None:
            raise Invalid("git-unavailable")
        self.executable = executable
        self.env = {"PATH": SAFE_PATH, "HOME": "/nonexistent", "LC_ALL": "C",
                    "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                    "GIT_NO_REPLACE_OBJECTS": "1", "GIT_NO_LAZY_FETCH": "1",
                    "GIT_GRAFT_FILE": os.devnull, "GIT_OPTIONAL_LOCKS": "0",
                    "GIT_TERMINAL_PROMPT": "0", "GIT_PAGER": "cat"}
        self.filter_overrides: list[str] = []
        # Even status may invoke clean/process filters. Enumerate configuration as
        # data before touching the index/worktree and neutralize every filter.
        keys = self.run("config", "--includes", "--null", "--name-only", "--get-regexp", r"^filter\.", missing_ok=True)
        for raw_key in keys.split(b"\0"):
            if raw_key:
                key = raw_key.decode("utf-8")
                suffix = key.rsplit(".", 1)[-1].lower()
                if suffix in {"clean", "smudge", "process", "required"}:
                    self.filter_overrides.extend(["-c", key + ("=false" if suffix == "required" else "=")])
        if Path(self.run("rev-parse", "--show-toplevel").decode().strip()).resolve() != self.repo:
            raise Invalid("repository-root-required")
        alternates = Path(self.run("rev-parse", "--git-path", "objects/info/alternates").decode().strip())
        if not alternates.is_absolute():
            alternates = self.repo / alternates
        if alternates.exists():
            raise Invalid("object-alternates-unsupported")

    def run(self, *args: str, missing_ok: bool = False) -> bytes:
        command = [self.executable, "--no-pager", "--no-replace-objects", "-c", "core.fsmonitor=false",
                   "-c", "core.hooksPath=" + os.devnull, "-c", "core.attributesFile=" + os.devnull,
                   "-c", "core.untrackedCache=false", "-c", "core.preloadIndex=false",
                   "-c", "protocol.allow=never", *self.filter_overrides, "-C", str(self.repo), *args]
        result = subprocess.run(command, env=self.env, stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL, timeout=30, check=False)
        if result.returncode and not (missing_ok and result.returncode == 1):
            raise Invalid("git-inspection-failed")
        return result.stdout

    def commit(self, value: str) -> str:
        if not OID.fullmatch(value):
            raise Invalid("full-commit-id-required")
        resolved = self.run("rev-parse", "--verify", value + "^{commit}").decode().strip()
        if resolved != value:
            raise Invalid("commit-identity-mismatch")
        return resolved

    def tree(self, value: str) -> str:
        return self.run("rev-parse", "--verify", value + "^{tree}").decode().strip()

    def blob(self, commit: str, path: str) -> bytes:
        size = int(self.run("cat-file", "-s", commit + ":" + path))
        if size > MAX_JSON:
            raise Invalid("configuration-too-large")
        return self.run("cat-file", "blob", commit + ":" + path)

    def state(self) -> dict[str, str]:
        return {"head": self.run("rev-parse", "HEAD").decode().strip(),
                "status_sha256": sha(self.run("status", "--porcelain=v1", "--untracked-files=all", "--ignore-submodules=all"))}

    def export(self, commit: str, destination: Path) -> dict[str, tuple[str, int]]:
        entries = self.run("ls-tree", "-rz", "--full-tree", commit).split(b"\0")
        total = 0
        expected: dict[str, tuple[str, int]] = {}
        if len(entries) > 20001:
            raise Invalid("snapshot-too-many-files")
        for entry in entries:
            if not entry:
                continue
            meta, raw_name = entry.split(b"\t", 1)
            mode, kind, oid = meta.decode("ascii").split()
            name = raw_name.decode("utf-8")
            if (mode not in {"100644", "100755"} or kind != "blob"
                    or name.startswith("/") or ".." in PurePosixPath(name).parts or "\\" in name
                    or ".git" in PurePosixPath(name).parts):
                raise Invalid("snapshot-entry-unsupported")
            size = int(self.run("cat-file", "-s", oid))
            total += size
            if total > 128 * 1024 * 1024:
                raise Invalid("snapshot-too-large")
            path = destination / name
            path.parent.mkdir(parents=True, exist_ok=True)
            data = self.run("cat-file", "blob", oid)
            with path.open("xb") as stream:
                stream.write(data)
            permission = 0o700 if mode == "100755" else 0o600
            path.chmod(permission)
            expected[name] = (sha(data), permission)
        return expected


def snapshot_stable(root: Path, expected: dict[str, tuple[str, int]]) -> bool:
    """Check tracked raw bytes/modes without following substituted symlinks."""
    try:
        if root.is_symlink():
            return False
        for name, (digest, permission) in expected.items():
            path = root / name
            current = root
            for part in PurePosixPath(name).parts:
                current = current / part
                if current.is_symlink():
                    return False
            if path.stat().st_mode & 0o777 != permission or sha(regular_bytes(path, 128 * 1024 * 1024)) != digest:
                return False
        return True
    except (OSError, Invalid):
        return False
