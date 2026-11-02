"""Read-only same-host boot clock metadata; never a target command."""
from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import subprocess
import sys
import time

from quality_trust import Invalid, regular_bytes, sha, outside_path

MODEL = "same-host-boot-ms-v1"
PRECISION_MS = 1
CONTINUITY_MS = 2000


@dataclass(frozen=True)
class Reading:
    wall_ms: int
    mono_ms: int
    boot_sha256: str


def read(*, protected_roots: list[Path]) -> Reading:
    if sys.platform == "linux":
        path = outside_path(Path("/proc/sys/kernel/random/boot_id"), protected_roots, strict=True, final_symlink=False)
        boot = regular_bytes(path, 256)
    elif sys.platform == "darwin":
        executable = outside_path(Path("/usr/sbin/sysctl"), protected_roots, strict=True)
        result = subprocess.run([str(executable), "-n", "kern.boottime"],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            env={"PATH": os.defpath, "LC_ALL": "C"}, timeout=2, check=False)
        if result.returncode or not result.stdout or len(result.stdout) > 256:
            raise Invalid("boot-clock-unavailable")
        boot = result.stdout
    else:
        raise Invalid("unsupported-local-clock")
    return Reading(time.time_ns() // 1000000, time.monotonic_ns() // 1000000, sha(boot))
