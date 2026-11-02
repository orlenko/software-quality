"""Trusted bootstrap primitives. No target imports, network or policy execution."""
from __future__ import annotations

from contextlib import contextmanager
from collections import deque
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import signal
import select
import stat
import subprocess
import sys
import time
import zipfile
from typing import Any, Iterator

VERSION = "0.1.2"
EXTERNAL_VERSION = "0.2.2"
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
    try:
        outside_path(path, [root])
    except Invalid as exc:
        if str(exc) == "path-traverses-protected-root":
            return True
        raise
    return False


def raw_absolute(path: Path) -> Path:
    """Capture caller context without erasing parents or following links."""
    return path if path.is_absolute() else Path.cwd() / path


def _walk_path(path: Path, roots: tuple[Path, ...], *, strict: bool,
               final_symlink: bool) -> Path:
    """Inspect each namespace hop; never normalize a selector before inspection."""
    if path.anchor not in ("", "/"):
        raise Invalid("unsupported-path-anchor")
    parts = path.parts if path.is_absolute() else (*Path.cwd().parts, *path.parts)
    pending = deque(parts[1:])
    current = Path("/")
    links = work = 0
    identities: set[tuple[int, int]] = set()
    for root in roots:
        try:
            info = root.lstat()
        except FileNotFoundError:
            continue  # Future creation roots retain lexical protection.
        except OSError:
            raise Invalid("protected-root-inspection-unavailable") from None
        identities.add((info.st_dev, info.st_ino))

    def protected(candidate: Path, info: os.stat_result | None = None) -> None:
        if (any(candidate.is_relative_to(root) for root in roots)
                or info is not None and (info.st_dev, info.st_ino) in identities):
            raise Invalid("path-traverses-protected-root")

    try:
        filesystem_root = current.lstat()
    except OSError:
        raise Invalid("filesystem-root-inspection-unavailable") from None
    protected(current, filesystem_root)
    while pending:
        work += 1
        if work > 512:
            raise Invalid("path-component-budget-exceeded")
        part = pending.popleft()
        if part == "..":
            # current was inspected before the step that could otherwise erase it.
            current = current.parent
            protected(current)
            continue
        candidate = current / part
        protected(candidate)
        try:
            info = candidate.lstat()
        except FileNotFoundError:
            if strict or ".." in pending:
                raise Invalid("required-path-or-parent-unavailable") from None
            # Creation callers may append only a new, ordinary directory tail.
            for component in pending:
                work += 1
                if work > 512:
                    raise Invalid("path-component-budget-exceeded")
                candidate /= component
                protected(candidate)
            return candidate
        except (OSError, ValueError):
            raise Invalid("path-inspection-unavailable") from None
        protected(candidate, info)
        if stat.S_ISLNK(info.st_mode):
            if not pending and not final_symlink:
                raise Invalid("terminal-symlink-refused")
            links += 1
            if links > 40:
                raise Invalid("path-symlink-budget-exceeded")
            try:
                destination = Path(os.readlink(candidate))
            except (OSError, ValueError):
                raise Invalid("path-link-unavailable") from None
            if destination.anchor not in ("", "/"):
                raise Invalid("unsupported-path-anchor")
            if destination.is_absolute():
                current = Path("/")
                protected(current, filesystem_root)
                pending.extendleft(reversed(destination.parts[1:]))
            else:
                pending.extendleft(reversed(destination.parts))
            continue
        if pending and not stat.S_ISDIR(info.st_mode):
            raise Invalid("path-ancestor-not-directory")
        current = candidate
    protected(current)
    return current


def outside_path(path: Path, roots: list[Path], *, strict: bool = False,
                 final_symlink: bool = True) -> Path:
    """Return a checked canonical path on a stable owner-controlled filesystem."""
    canonical_roots = tuple(_walk_path(root, (), strict=False, final_symlink=True) for root in roots)
    return _walk_path(path, canonical_roots, strict=strict, final_symlink=final_symlink)


def runtime_python(roots: list[Path]) -> str:
    path = outside_path(Path(sys.executable), roots, strict=True)
    if not path.is_file() or not os.access(path, os.X_OK):
        raise Invalid("approved-interpreter-unavailable")
    return str(path)


def subject_root(path: Path) -> Path:
    root = outside_path(path, [], strict=True)
    if not root.is_dir():
        raise Invalid("subject-directory-required")
    return root


def selector_context(arguments: list[str], *, subjectless_install: bool = False) -> tuple[Path | None, list[str]]:
    """Extract one unambiguous subject; leave launcher policy to its own parser."""
    result = list(arguments)
    found: tuple[int, str, bool] | None = None
    index = 0
    while index < len(result):
        token = result[index]
        option = token.split("=", 1)[0]
        if token == "--" or option in ("--r", "--re", "--rep"):
            raise Invalid("ambiguous-subject-argument")
        if option == "--repo":
            if found is not None:
                raise Invalid("duplicate-subject-argument")
            equals = "=" in token
            if equals:
                value = token.split("=", 1)[1]
            else:
                index += 1
                if index >= len(result):
                    raise Invalid("missing-subject-argument")
                value = result[index]
            if not value or value.startswith("-"):
                raise Invalid("ambiguous-subject-argument")
            found = (index, value, equals)
        index += 1
    if found is None:
        prefix = 2 if result[:1] == ["--adapter-protocol"] else 1 if result and result[0].startswith("--adapter-protocol=") else 0
        if subjectless_install and len(result) > prefix and result[prefix] == "install":
            return None, result
        raise Invalid("explicit-subject-argument-required")
    position, spelling, equals = found
    repo = subject_root(Path(spelling))
    result[position] = ("--repo=" if equals else "") + str(repo)
    return repo, result


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
        self.repo = subject_root(repo)
        executable = shutil.which("git", path=SAFE_PATH)
        if executable is None:
            raise Invalid("git-unavailable")
        self.executable = str(outside_path(Path(executable), [self.repo], strict=True))
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
        reported = subject_root(Path(self.run("rev-parse", "--show-toplevel").decode().strip()))
        if not (within(reported, self.repo) and within(self.repo, reported)):
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


class Cancellation:
    """Owned request data. Signal handlers never reap or signal a child."""
    def __init__(self) -> None:
        self.signum: int | None = None
        self.active = False

    @property
    def requested(self) -> bool:
        return self.signum is not None

    def request(self, signum: int, frame: object = None) -> None:
        if self.signum is None:
            self.signum = signum

    @contextmanager
    def handlers(self) -> Iterator[None]:
        if self.active:
            yield
            return
        previous: dict[int, Any] = {}
        try:
            for signum in (signal.SIGINT, signal.SIGTERM):
                previous[signum] = signal.signal(signum, self.request)
            self.active = True
            yield
        finally:
            self.active = False
            for signum, handler in previous.items():
                signal.signal(signum, handler)


class OwnedProcess:
    """One new session, one unreaped identity, signals before explicit release.

    Callers must hold Cancellation.handlers through spawn, cleanup and handoff.
    Never expose a signal-capable Popen to an outside reaper.
    """
    _capability_verified = False

    def __init__(self, cancellation: Cancellation, *, protected_roots: list[Path]) -> None:
        self.cancellation = cancellation
        self.protected_roots = list(protected_roots)
        self._process: subprocess.Popen[bytes] | None = None
        self._authority = False
        self._ended = False
        self._unknown = False
        self.reaped = False
        self.code: int | None = None
        self.cleanup_complete = False
        self.signal_unavailable = False

    @property
    def pid(self) -> int:
        if self._process is None:
            raise Invalid("owned-process-not-started")
        return self._process.pid

    @property
    def stdout(self) -> Any:
        return self._process.stdout if self._process is not None else None

    @staticmethod
    def _status(info: Any, pid: int) -> int:
        if info.si_pid != pid:
            raise Invalid("owned-child-identity-mismatch")
        if info.si_code == os.CLD_EXITED:
            return int(info.si_status)
        if info.si_code in (os.CLD_KILLED, os.CLD_DUMPED):
            return -int(info.si_status)
        raise Invalid("unsupported-child-observation")

    @classmethod
    def require_capability(cls, cancellation: Cancellation, *, protected_roots: list[Path]) -> None:
        required = ("waitid", "P_PID", "WEXITED", "WNOHANG", "WNOWAIT", "CLD_EXITED", "CLD_KILLED", "CLD_DUMPED", "killpg")
        if (os.name != "posix" or not cancellation.active
                or not all(hasattr(os, name) for name in required)
                or not callable(getattr(os, "waitid", None))
                or signal.getsignal(signal.SIGCHLD) != signal.SIG_DFL):
            raise Invalid("nonreaping-process-capability-unavailable")
        interpreter = runtime_python(protected_roots)
        if cls._capability_verified:
            return
        # Known bounded interpreter code only; no target and no unproved signal.
        probe = cls(cancellation, protected_roots=protected_roots)
        probe._spawn([interpreter, "-I", "-S", "-c", "pass"],
                     env={"PATH": os.defpath, "HOME": "/nonexistent", "LC_ALL": "C"},
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        valid = False
        try:
            until = time.monotonic() + 2
            while time.monotonic() < until:
                if probe.observe() is not None:
                    valid = probe.code == 0
                    break
                time.sleep(0.005)
        finally:
            probe._authority = False
            probe._ended = True
            probe._reap(2)
            if not probe.reaped and probe._process is not None:
                # Unsupported waitid must not leak the known benign probe. This
                # is a non-signaling owned wait, never authority to kill a PID.
                until = time.monotonic() + 2
                while time.monotonic() < until:
                    try:
                        pid, status = os.waitpid(probe.pid, os.WNOHANG)
                    except OSError:
                        break
                    if pid == probe.pid:
                        probe.reaped = True
                        probe._process.returncode = os.waitstatus_to_exitcode(status)
                        break
                    time.sleep(0.005)
        if not valid or not probe.reaped or probe._unknown:
            raise Invalid("nonreaping-process-probe-incomplete")
        cls._capability_verified = True

    def _spawn(self, argv: list[str], **kwargs: Any) -> None:
        if self._process is not None or self._ended:
            raise Invalid("owned-process-already-started")
        self._process = subprocess.Popen(argv, start_new_session=True, **kwargs)
        self._authority = True

    def start(self, argv: list[str], **kwargs: Any) -> None:
        self.require_capability(self.cancellation, protected_roots=self.protected_roots)
        if self.cancellation.requested:
            raise KeyboardInterrupt
        self._spawn(argv, **kwargs)

    def observe(self) -> int | None:
        if not self._authority or self._ended or self._process is None:
            raise Invalid("owned-signal-authority-ended")
        if self._process.returncode is not None:
            self._authority = False
            self._unknown = True
            raise Invalid("owned-child-reaped-externally")
        try:
            info = os.waitid(os.P_PID, self.pid, os.WEXITED | os.WNOHANG | os.WNOWAIT)
            if info is not None:
                self.code = self._status(info, self.pid)
        except (OSError, Invalid, AttributeError, TypeError):
            self._authority = False
            self._unknown = True
            raise Invalid("owned-child-observation-unavailable") from None
        return self.code

    def send(self, signum: int) -> bool:
        self.observe()  # A completed WNOWAIT child still reserves its numeric ID.
        if not self._authority:
            return False
        try:
            os.killpg(self.pid, signum)
            return True
        except ProcessLookupError:
            return True  # Attempt found no group; cleanup still needs own wait/absence.
        except OSError:
            self.signal_unavailable = True
            return False  # EPERM is not absence; no Popen.kill/poll fallback.

    def _reap(self, seconds: float) -> None:
        if self._process is None or self.reaped or self._unknown:
            return
        until = time.monotonic() + seconds
        while time.monotonic() < until:
            try:
                info = os.waitid(os.P_PID, self.pid, os.WEXITED | os.WNOHANG)
                if info is not None:
                    code = self._status(info, self.pid)
                    self.reaped = True
                    self.code = code
                    self._process.returncode = code  # Only AFTER the real reaping wait.
                    return
            except (OSError, Invalid, AttributeError, TypeError):
                self._unknown = True
                return
            time.sleep(0.005)

    def close(self) -> bool:
        if self._ended:
            return self.cleanup_complete
        try:
            if self._process is not None and self._authority:
                self.send(signal.SIGKILL)
        finally:
            # No later path may signal, including if the actual wait is interrupted.
            self._authority = False
            self._ended = True
            self._reap(2)
            if self._process is not None and self.reaped and not self._unknown:
                until = time.monotonic() + 2
                while True:
                    try:
                        os.killpg(self.pid, 0)  # Non-signaling observation only.
                    except ProcessLookupError:
                        self.cleanup_complete = True
                        break
                    except OSError:
                        break
                    if time.monotonic() >= until:
                        break
                    time.sleep(0.005)
        return self.cleanup_complete

    def wait(self, cancellation_grace: float = 35) -> int | None:
        forwarded = False
        until: float | None = None
        try:
            while self.observe() is None:
                if self.cancellation.requested and not forwarded:
                    self.send(self.cancellation.signum or signal.SIGINT)
                    forwarded = True
                    until = time.monotonic() + cancellation_grace
                if until is not None and time.monotonic() >= until:
                    break
                time.sleep(0.01)
        finally:
            self.close()
        return self.code


class OutputUnavailable(OSError):
    def __init__(self, partial: int) -> None:
        super().__init__("bounded-output-unavailable")
        self.partial = partial


def write_output(data: bytes, cancellation: Cancellation, *, fd: int = 1,
                 seconds: float = 2, known_failure: bool = False, allow_cancelled: bool = False) -> None:
    """Bound delivery; never let a full pipe hide handled cancellation forever."""
    offset = 0
    blocking = os.get_blocking(fd)
    try:
        os.set_blocking(fd, False)
        until = time.monotonic() + seconds
        while offset < len(data):
            if (cancellation.requested and not (known_failure or allow_cancelled)) or time.monotonic() >= until:
                raise OutputUnavailable(offset)
            if not select.select([], [fd], [], min(0.05, max(0, until-time.monotonic())))[1]:
                continue
            try:
                written = os.write(fd, data[offset:offset+65536])
            except BlockingIOError:
                continue
            if written <= 0:
                raise OutputUnavailable(offset)
            offset += written
    except OSError as exc:
        if isinstance(exc, OutputUnavailable):
            raise
        raise OutputUnavailable(offset) from exc
    finally:
        os.set_blocking(fd, blocking)


def diagnostic(message: str, cancellation: Cancellation) -> None:
    try:
        write_output((message + "\n").encode(), cancellation, fd=2, seconds=0.1, known_failure=True)
    except (OSError, KeyboardInterrupt):
        pass
