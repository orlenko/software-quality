"""Owned evidence primitives shared by versioned orchestrators."""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import os
from pathlib import Path
from typing import Any, Iterator
import uuid

from quality_trust import Invalid, canonical, sha
from quality.schema import checked


def sync_directory(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def stage(name: str, status: str = "incomplete", reason: str = "not-run",
          code: int = -1, log: str = "") -> dict[str, Any]:
    return {"id": name, "status": status, "reason": reason, "exit_code": code, "log": log}


def verdict(stages: list[dict[str, Any]]) -> str:
    values = {item["status"] for item in stages}
    return "fail" if "fail" in values else "incomplete" if "incomplete" in values else "pass"


def save(path: Path, report: dict[str, Any], schema: str = "report") -> None:
    checked(schema, report)
    temporary = path.with_name(".report-" + uuid.uuid4().hex)
    try:
        fd = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(canonical(report))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        sync_directory(path.parent)
    finally:
        temporary.unlink(missing_ok=True)


@contextmanager
def target_lock(state: Path, repo: Path) -> Iterator[None]:
    lock = state / ("target-" + sha(os.fsencode(repo)) + ".lock")
    fd = os.open(lock, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "r+b") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise Invalid("target-run-already-active") from exc
        yield
