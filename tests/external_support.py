"""Invented JSON facts and plain-text Git subjects, never an executable producer."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import os
import subprocess
import sys
from typing import Any

from quality_trust import EXTERNAL_VERSION, canonical, parse_json, sha
from quality.external_clock import Reading

ROOT = Path(__file__).resolve().parents[1]
D = "a" * 64


def config() -> dict[str, Any]:
    return {"schema_version": 2, "repository": "example/invented",
        "gate": {"id": "canonical", "producer_id": "invented-producer", "observer_id": "invented-observer",
            "canonical_sha256": D, "coverage_sha256": D, "environment_sha256": D,
            "mechanism": {"id": "immutable-tree", "sha256": D},
            "observer": {"profile_sha256": D, "mechanism_sha256": D},
            "trust_rule": "owner-designation-permitted", "required_controls": ["deadline", "cleanup"],
            "allowed_effects": ["read-source"], "refs": ["refs/heads/main"],
            "budget_seconds": 10, "import_window_seconds": 60}, "unsupported_obligations": []}


class Fixture:
    def __init__(self, root: Path, package: Path, digest: str, source: str, settings: dict[str, Any] | None = None) -> None:
        self.root, self.package, self.digest, self.source = root.resolve(), package, digest, source
        self.repo, self.cache, self.state = self.root / "subject", self.root / "cache", self.root / "state"
        self.repo.mkdir()
        self.config = deepcopy(settings) if settings is not None else config()
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Invented Example")
        self.git("config", "user.email", "invented@example.invalid")
        self.write("README.txt", "Newly authored invented plain-text subject.\n")
        self.write(".quality/config.json", canonical(self.config))
        self.write(".quality/lock.json", canonical({"schema_version": 2, "publisher": "orlenko/software-quality",
            "source": source, "artifact_sha256": digest, "version": EXTERNAL_VERSION, "policy_version": "0.1"}))
        self.head = self.base = self.commit()
        result = self.command("install", "--artifact", str(package), "--sha256", digest,
                              "--source", source, "--cache", str(self.cache))
        if result.returncode:
            raise AssertionError(result.stderr)

    def write(self, name: str, value: str | bytes) -> Path:
        path = self.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(value.encode() if isinstance(value, str) else value)
        return path

    def git(self, *args: str) -> str:
        result = subprocess.run(["git", "-C", str(self.repo), *args], env={"PATH": os.defpath, "HOME": str(self.root),
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "LC_ALL": "C"},
            capture_output=True, text=True, check=True, timeout=30)
        return result.stdout.strip()

    def commit(self) -> str:
        self.git("add", ".")
        self.git("-c", "core.hooksPath=" + os.devnull, "commit", "-m", "Invented fixture")
        return self.git("rev-parse", "HEAD")

    def command(self, *args: str, shim: bool = False) -> subprocess.CompletedProcess[str]:
        entry = ROOT / ("adapters/quality_external.py" if shim else "quality_external_launch.py")
        return subprocess.run([sys.executable, "-I", "-S", str(entry), *args],
            capture_output=True, text=True, timeout=60, env={"PATH": os.defpath, "LC_ALL": "C"})

    def run(self, verb: str, *extra: str, trusted: bool = True, shim: bool = False) -> tuple[subprocess.CompletedProcess[str], dict[str, Any] | None]:
        args = [verb, "--repo", str(self.repo), "--base", self.base, "--head", self.head,
                "--identity", "example/invented", "--cache", str(self.cache), "--state", str(self.state)]
        if trusted:
            args.extend(["--trusted-head", self.head])
        result = self.command(*args, *extra, shim=shim)
        return result, parse_json(result.stdout.encode()) if result.stdout.startswith("{") else None

    def plan(self, **kwargs: Any) -> dict[str, Any]:
        result, output = self.run("doctor", **kwargs)
        if result.returncode != 2 or output is None:
            raise AssertionError(result.stderr + result.stdout)
        return parse_json(Path(output["record"]).read_bytes())

    def facts(self, plan: dict[str, Any], code: int = 0) -> tuple[dict[str, Any], dict[str, Any]]:
        gate = self.config["gate"]
        at = plan["issued_wall_ms"]
        mono = plan["issued_mono_ms"]
        record = {"gate_id": gate["id"], "producer_id": gate["producer_id"], "invocation_id": "invented-invocation",
            "canonical_sha256": gate["canonical_sha256"], "phase": "known-commit", "features": [],
            "coverage": {"kind": "whole", "sha256": gate["coverage_sha256"]},
            "consumed": {"mechanism_id": gate["mechanism"]["id"], "mechanism_sha256": gate["mechanism"]["sha256"],
                "established": True, "before_context_sha256": plan["context_sha256"], "after_context_sha256": plan["context_sha256"],
                "origin_tree": plan["context"]["head_tree"], "environment_sha256": gate["environment_sha256"], "provenance": "trusted-local"},
            "outcome": {"kind": "completed", "exit_code": code}, "timing": {"clock": plan["context"]["clock"],
                "started_ms": at + 1, "finished_ms": at + 2, "started_mono_ms": mono + 1, "finished_mono_ms": mono + 2, "elapsed_ms": 1},
            "effects": ["read-source"], "output_complete": True, "note": "Invented facts; no producer executed."}
        envelope = {"schema_version": 2, "protocol": "external-checks-v1", "plan_id": plan["plan_id"],
            "challenge": plan["challenge"], "context_sha256": plan["context_sha256"], "records": [record]}
        observer = {"schema_version": 2, "protocol": "external-controls-v1", "plan_id": plan["plan_id"],
            "challenge": plan["challenge"], "context_sha256": plan["context_sha256"], "gate_id": gate["id"],
            "invocation_id": record["invocation_id"], "observer_id": gate["observer_id"],
            "profile_sha256": gate["observer"]["profile_sha256"], "mechanism_sha256": gate["observer"]["mechanism_sha256"],
            "source_route": "independent-controller", "basis": "controller-observation", "clock": plan["context"]["clock"],
            "deadline_at_ms": at + 1 + gate["budget_seconds"] * 1000, "cleanup_state": "complete",
            "observed_from_mono_ms": mono, "observed_through_mono_ms": mono + 3, "cleanup_at_mono_ms": mono + 2,
            "deadline_at_mono_ms": mono + 1 + gate["budget_seconds"] * 1000, "observed_from_ms": at, "observed_through_ms": at + 3, "cleanup_at_ms": at + 2,
            "observations": [{"kind": kind, "state": "enforced", "measurement_ref": "invented-controller-fact"}
                             for kind in gate["required_controls"]]}
        return envelope, observer

    def inputs(self, envelope: Any, observer: Any | None) -> list[str]:
        receipt = self.root / "receipt.json"
        data = envelope if isinstance(envelope, bytes) else canonical(envelope)
        receipt.write_bytes(data)
        args = ["--evidence", str(receipt), "--evidence-sha256", sha(data), "--approved-producer", self.config["gate"]["producer_id"]]
        if observer is not None:
            receipt = self.root / "observer.json"
            data = observer if isinstance(observer, bytes) else canonical(observer)
            receipt.write_bytes(data)
            args += ["--observations", str(receipt), "--observations-sha256", sha(data), "--approved-observer", self.config["gate"]["observer_id"]]
        return args

    def receive(self, plan: dict[str, Any], envelope: Any, observer: Any | None, **kwargs: Any) -> tuple[subprocess.CompletedProcess[str], dict[str, Any] | None]:
        return self.run("import", "--plan", plan["plan_id"], *self.inputs(envelope, observer), **kwargs)

    def clock(self, plan: dict[str, Any], delta: int = 100) -> Reading:
        return Reading(plan["issued_wall_ms"] + delta, plan["issued_mono_ms"] + delta, plan["context"]["clock"]["boot_sha256"])
