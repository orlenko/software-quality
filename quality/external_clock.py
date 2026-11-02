"""Read-only same-host boot clock metadata; never a target command."""
from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import subprocess
import sys
import time

from quality_trust import Invalid, regular_bytes, sha

MODEL = "same-host-boot-ms-v1"
PRECISION_MS = 1
CONTINUITY_MS = 2000


@dataclass(frozen=True)
class Reading:
    wall_ms: int
    mono_ms: int
    boot_sha256: str


def read() -> Reading:
    if sys.platform == "linux":
        boot = regular_bytes(Path("/proc/sys/kernel/random/boot_id"), 256)
    elif sys.platform == "darwin":
        result = subprocess.run(["/usr/sbin/sysctl", "-n", "kern.boottime"],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            env={"PATH": os.defpath, "LC_ALL": "C"}, timeout=2, check=False)
        if result.returncode or not result.stdout or len(result.stdout) > 256:
            raise Invalid("boot-clock-unavailable")
        boot = result.stdout
    else:
        raise Invalid("unsupported-local-clock")
    return Reading(time.time_ns() // 1000000, time.monotonic_ns() // 1000000, sha(boot))
