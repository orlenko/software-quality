"""Owned evidence primitives shared by versioned orchestrators."""
from __future__ import annotations

from contextlib import contextmanager, ExitStack
from datetime import datetime, timezone
import fcntl
import os
import stat
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


class SaveFailure(OSError):
    def __init__(self, published: bool | None, durable: bool, cleanup_failed: bool, interrupted: bool) -> None:
        super().__init__("atomic-evidence-save-unconfirmed")
        self.published = published
        self.durable = durable
        self.cleanup_failed = cleanup_failed
        self.interrupted = interrupted


def save(path: Path, report: dict[str, Any], schema: str = "report") -> None:
    checked(schema, report)
    temporary = path.with_name(".report-" + uuid.uuid4().hex)
    published: bool | None = False
    durable = cleanup_failed = interrupted = False
    error: BaseException | None = None
    try:
        fd = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(canonical(report))
            stream.flush()
            os.fsync(stream.fileno())
        published = None  # Publication becomes uncertain before the replacing syscall.
        os.replace(temporary, path)
        published = True
        sync_directory(path.parent)
        durable = True
    except (OSError, ValueError, KeyboardInterrupt) as exc:
        error = exc
        interrupted = isinstance(exc, KeyboardInterrupt)
    finally:
        try:
            temporary.unlink(missing_ok=True)
        except (OSError, KeyboardInterrupt) as exc:
            cleanup_failed = True
            interrupted = interrupted or isinstance(exc, KeyboardInterrupt)
            if error is None:
                error = exc
    if error is not None:
        # A visible replacement is never rolled back after a sync/cleanup error.
        raise SaveFailure(published, durable, cleanup_failed, interrupted) from error


@contextmanager
def _descriptor(path: Path, flags: int) -> Iterator[int]:
    fd = os.open(path, flags, 0o600)
    try:
        yield fd
    finally:
        os.close(fd)


def _private_regular(info: os.stat_result) -> None:
    if not stat.S_ISREG(info.st_mode) or info.st_mode & 0o077 or info.st_uid != os.geteuid():
        raise Invalid("private-regular-lock-required")


@contextmanager
def target_lock(state: Path, repo: Path) -> Iterator[None]:
    with ExitStack() as resources:
        directory = resources.enter_context(_descriptor(repo, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW))
        info = os.fstat(directory)
        if not stat.S_ISDIR(info.st_mode):
            raise Invalid("lock-directory-required")
        identity = sha(canonical([info.st_dev, info.st_ino]))
        locks = (state / ("target-object-v1-" + identity + ".lock"),
                 state / ("target-" + sha(os.fsencode(repo)) + ".lock"))
        for lock in locks:
            try:
                _private_regular(lock.lstat())
            except FileNotFoundError:
                pass
            fd = resources.enter_context(_descriptor(lock, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK))
            _private_regular(os.fstat(fd))
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise Invalid("target-run-already-active") from exc
        yield
