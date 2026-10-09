"""Opt-in Quartermaster control plane over existing live Revbench custody.

No harness substitution, evidence registration, provider collection or budget
arithmetic lives here. Immutable sidecars retain authentic local observations;
the one authoritative resource state remains the designated Quartermaster home.
"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from datetime import UTC, datetime
from typing import Any, Mapping

from caplab.catalog.projection import load_projection
from caplab.catalog.preparation import select_entry, validate_against_spec
from caplab.runtime.canonical import canonical_json, sha256_hex
from caplab.revbench.process_tree import namespace_init, boot_id
from caplab.revbench.custody import (
    LiveExecutionCustodyError,
    FreshProcessCapture,
    _read_canonical_document,
    _write_exclusive,
)

SCHEMA = "caplab-shared-admission-enrollment/1"
PINNED_SCHEMA = "caplab-shared-admission-enrollment/2"
MAX_BYTES = 16 * 1024 * 1024
RESPONSE = "quartermaster-shared-admission-response/2"


class SharedAdmissionControlError(LiveExecutionCustodyError):
    """A reported or uncertain control-plane failure; never a launch permission."""


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _clock_sample() -> dict:
    return {"utc": _now(), "monotonic_ns": time.monotonic_ns(), "boot_id": boot_id()}


def _interval(before: dict | None, after: dict | None, source_id: str) -> dict | None:
    if before is None or after is None:
        return None
    if (
        before["boot_id"] != after["boot_id"]
        or before["monotonic_ns"] > after["monotonic_ns"]
        or datetime.fromisoformat(before["utc"]) > datetime.fromisoformat(after["utc"])
    ):
        return None
    preimage = {"before": before, "after": after}
    return {
        "schema": "quartermaster-time-interval/1",
        "lower": before["utc"],
        "upper": after["utc"],
        "lower_inclusive": True,
        "upper_inclusive": True,
        "clock_domain": "UTC",
        "clock_id": "host-utc:" + before["boot_id"],
        "precision_microseconds": 1,
        "provenance": {
            "source_id": source_id,
            "sha256": "sha256:" + sha256_hex(canonical_json(preimage)),
        },
    }


def _read(path: Path) -> bytes:
    data = path.read_bytes()
    if len(data) > MAX_BYTES:
        raise LiveExecutionCustodyError("shared_admission_input_too_large")
    return data


def _pinned(path: str, digest: str) -> Path:
    location = Path(path)
    if not location.is_absolute() or sha256_hex(_read(location)) != digest:
        raise LiveExecutionCustodyError("shared_admission_input_pin_changed")
    return location


def _retain(root: Path, name: str, document: Mapping[str, Any]) -> dict:
    owned = json.loads(canonical_json(document))
    try:
        retained = _read_canonical_document(root / name)
    except FileNotFoundError:
        _write_exclusive(root, name, canonical_json(owned))
        return owned
    if retained != owned:
        raise LiveExecutionCustodyError("shared_admission_custody_conflict")
    return retained


class SharedAdmissionEnrollment:
    """Explicit local enrollment; identities are assertions, not authentication."""

    def __init__(self, document: Mapping[str, Any]):
        if not isinstance(document, Mapping):
            raise LiveExecutionCustodyError("shared_admission_enrollment_invalid")
        self.document = json.loads(canonical_json(document))
        d = self.document
        fields = {
            "schema_version",
            "cli",
            "cli_sha256",
            "home",
            "home_id",
            "release_path",
            "release_sha256",
            "overlay_path",
            "overlay_sha256",
            "policy_path",
            "policy_sha256",
            "observations_path",
            "entry",
            "caller_id",
            "custody_domain_id",
            "binding_id",
            "credential_profile_sha256",
        }
        if d.get("schema_version") == PINNED_SCHEMA:
            fields.add("sdk_source_tree_sha256")
        if set(d) != fields or d["schema_version"] not in {SCHEMA, PINNED_SCHEMA}:
            raise LiveExecutionCustodyError("shared_admission_enrollment_invalid")
        if not all(isinstance(d[k], str) and d[k] for k in fields):
            raise LiveExecutionCustodyError("shared_admission_enrollment_invalid")
        for field in ("home", "observations_path"):
            if not Path(d[field]).is_absolute():
                raise LiveExecutionCustodyError("shared_admission_path_invalid")
        self.check_pins()
        self.projection = load_projection(
            Path(d["release_path"]), Path(d["overlay_path"]), [d["cli"]]
        )
        self.selection = select_entry(self.projection, d["entry"])
        if self.selection.entry.get("account_id") != self.selection.profile.get(
            "account_id"
        ):
            raise LiveExecutionCustodyError("shared_admission_profile_account_mismatch")
        if self.selection.entry.get("enabled") is not True:
            raise LiveExecutionCustodyError("shared_admission_catalog_entry_disabled")
        self.policy = json.loads(_read(Path(d["policy_path"])))
        self.capabilities = self._capabilities()
        if not (
            "quartermaster-time-interval/1"
            in self.capabilities.get("time_evidence_schemas", [])
            and RESPONSE in self.capabilities.get("response_protocols", [])
            and self.capabilities.get("incident_reconciliation")
            == "quartermaster-shared-admission-effect/3"
        ):
            raise LiveExecutionCustodyError("shared_admission_sdk_incompatible")

    def _capabilities(self) -> dict:
        try:
            raw = subprocess.run(
                [self.document["cli"], "admission", "capabilities"],
                capture_output=True,
                stdin=subprocess.DEVNULL,
                env={},
                cwd="/",
                timeout=10,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            raise SharedAdmissionControlError(
                "shared_admission_capability_probe_unavailable"
            ) from error
        if raw.returncode != 0:
            raise SharedAdmissionControlError("shared_admission_capability_probe_failed")
        if len(raw.stdout) > MAX_BYTES:
            raise SharedAdmissionControlError(
                "shared_admission_capability_reply_too_large"
            )
        try:
            capabilities = json.loads(raw.stdout)
        except (ValueError, UnicodeError) as error:
            raise SharedAdmissionControlError(
                "shared_admission_capability_reply_invalid"
            ) from error
        if (
            not isinstance(capabilities, dict)
            or capabilities.get("schema")
            != "quartermaster-shared-admission-capabilities/1"
        ):
            raise LiveExecutionCustodyError("shared_admission_sdk_incompatible")
        expected = self.document.get("sdk_source_tree_sha256")
        if expected is not None and expected != capabilities.get("source_tree_sha256"):
            raise LiveExecutionCustodyError("shared_admission_sdk_pin_changed")
        return capabilities

    def validate_deadline(self, deadline: str) -> None:
        """Check fixed-window fit without altering the native authority deadline."""
        account = next(
            a
            for a in self.projection.release["catalog"]["accounts"]
            if a["id"] == self.selection.entry["account_id"]
        )
        joined = set(account["quota_pool_ids"])
        try:
            end = datetime.fromisoformat(deadline)
            for budget in self.policy["launch_budgets"]:
                if budget["pool_id"] not in joined:
                    continue
                for window in budget["windows"]:
                    if window["kind"] == "fixed" and not (
                        datetime.fromisoformat(window["start"])
                        < end
                        <= datetime.fromisoformat(window["end"])
                    ):
                        raise LiveExecutionCustodyError(
                            "shared_admission_deadline_incompatible"
                        )
        except LiveExecutionCustodyError:
            raise
        except (KeyError, TypeError, ValueError) as error:
            raise LiveExecutionCustodyError(
                "shared_admission_policy_invalid"
            ) from error

    @classmethod
    def read(cls, path: Path) -> SharedAdmissionEnrollment:
        return cls(json.loads(_read(Path(path))))

    def check_pins(self) -> None:
        d = self.document
        for name in ("cli", "release", "overlay", "policy"):
            _pinned(
                d["cli"] if name == "cli" else d[name + "_path"], d[name + "_sha256"]
            )
        if hasattr(self, "capabilities") and self._capabilities() != self.capabilities:
            raise LiveExecutionCustodyError("shared_admission_sdk_pin_changed")

    def validate_binding(
        self, manifest: Mapping[str, Any], registrar: Any, domain: str
    ) -> None:
        d = self.document
        if (
            domain != d["custody_domain_id"]
            or manifest["binding"]["binding_id"] != d["binding_id"]
        ):
            raise LiveExecutionCustodyError("shared_admission_native_identity_mismatch")
        validate_against_spec(self.selection, manifest, registrar)
        runtime = json.loads(
            registrar.resolve(manifest["binding"]["configuration"]["runtime_ref"])
        )
        profile_ref = runtime["credential_profile_ref"]
        profile_bytes = registrar.resolve(profile_ref)
        if sha256_hex(profile_bytes) != d["credential_profile_sha256"]:
            raise LiveExecutionCustodyError(
                "shared_admission_credential_profile_mismatch"
            )

    def bind_session(self, session: Any) -> None:
        if (
            session.intent["custody_domain_id"] != self.document["custody_domain_id"]
            or session.intent["binding_id"] != self.document["binding_id"]
        ):
            raise LiveExecutionCustodyError("shared_admission_native_identity_mismatch")
        path = session.root / "shared-admission-enrollment.json"
        if session.resumed and not path.exists():
            raise LiveExecutionCustodyError("shared_admission_late_enrollment_refused")
        _retain(session.root, path.name, self.document)

    def capture(self, capture: Any) -> ProcessAdmission:
        return ProcessAdmission(self, capture)

    def reconcile_session(self, session: Any) -> list[dict | None]:
        """Reconcile retained native facts even after sealing, without acquiring rights."""
        self.bind_session(session)
        return [
            self.capture(p).reconcile(p.completion)
            for p in session.retained_processes()
        ]


def require_retained_enrollment(
    session: Any, enrollment: SharedAdmissionEnrollment | None
) -> None:
    if enrollment is None:
        if (session.root / "shared-admission-enrollment.json").exists():
            raise LiveExecutionCustodyError(
                "shared_admission_retained_enrollment_required"
            )
    else:
        enrollment.bind_session(session)


class _AssignedLaunchAdmission:
    """One native assigned right, one shared allocation; replay never invokes."""

    def __init__(self, enrollment: SharedAdmissionEnrollment, capture: Any):
        self.enrollment = enrollment
        self.capture = capture
        self.root = capture.custody_root
        if self.root is None:
            raise LiveExecutionCustodyError("shared_admission_custody_root_missing")
        self.record = None
        self.fresh_permit = False
        self.namespace_witness = None
        self.last_alive_at = None
        self.last_alive_sample = None
        self.post_monitor_observation_ms = None

    def adopt_namespace(self, witness, *, post_monitor_timeout_ms: int) -> None:
        # Called only by the prospective pinned readiness administration. This
        # descriptor is already bound to the actual direct child PID1.
        if post_monitor_timeout_ms != 1000 or self.namespace_witness is not None:
            raise LiveExecutionCustodyError("shared_admission_readiness_invalid")
        self.namespace_witness = witness
        self.post_monitor_observation_ms = post_monitor_timeout_ms
        _retain(self.root, "shared-admission-namespace-init.json", witness.fact)

    def sample_clock(self) -> dict:
        return _clock_sample()

    def _call(self, verb: str, **fields: Any) -> dict:
        d = self.enrollment.document
        self.enrollment.check_pins()
        argv = [
            d["cli"],
            "admission",
            verb,
            "--home",
            d["home"],
            "--home-id",
            d["home_id"],
            "--now",
            _now(),
            "--json-protocol",
            RESPONSE,
        ]
        for name, value in fields.items():
            if name == "require_fresh":
                if value is True:
                    argv.append("--require-fresh")
                continue
            if name in {
                "request",
                "policy",
                "catalog",
                "observations",
                "evidence",
                "ended_between",
            }:
                body = (
                    self.enrollment.projection.release_bytes
                    if name == "catalog"
                    else value
                    if isinstance(value, bytes)
                    else canonical_json(value)
                )
                filename = "shared-input-" + sha256_hex(body) + ".json"
                self._retain_list(filename, body)
                value = str(self.root / filename)
            argv.extend(["--" + name.replace("_", "-"), str(value)])
        try:
            completed = subprocess.run(
                argv,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                env={},
                cwd="/",
                timeout=60,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            raise SharedAdmissionControlError(
                "shared_admission_transport_uncertain"
            ) from error
        if len(completed.stdout) > MAX_BYTES or len(completed.stderr) > MAX_BYTES:
            raise SharedAdmissionControlError("shared_admission_reply_too_large")
        raw = {
            "verb": verb,
            "argv": argv,
            "exit_code": completed.returncode,
            "stdout_hex": completed.stdout.hex(),
            "stderr_hex": completed.stderr.hex(),
        }
        _retain(
            self.root,
            "shared-transport-" + sha256_hex(canonical_json(raw)) + ".json",
            raw,
        )
        try:
            envelope = json.loads(completed.stdout)
        except (ValueError, UnicodeError) as error:
            raise SharedAdmissionControlError(
                "shared_admission_reply_invalid"
            ) from error
        if not isinstance(envelope, dict) or envelope.get("schema") != RESPONSE:
            raise SharedAdmissionControlError("shared_admission_protocol_invalid")
        if set(envelope) == {"schema", "error"}:
            error = envelope["error"]
            if not isinstance(error, dict) or set(error) != {"code", "type", "message"}:
                raise SharedAdmissionControlError("shared_admission_protocol_invalid")
            expected = 4 if error["code"] == "admission_busy" else 2
            if completed.returncode != expected:
                raise SharedAdmissionControlError("shared_admission_protocol_invalid")
            raise SharedAdmissionControlError("shared_admission_" + str(error["code"]))
        if set(envelope) != {"schema", "result"}:
            raise SharedAdmissionControlError("shared_admission_protocol_invalid")
        result = envelope["result"]
        statuses = {
            "admitted": 0,
            "prepared": 0,
            "recorded": 0,
            "closed": 0,
            "settled": 0,
            "reconciled": 0,
            "existing": 0,
            "refuse": 3,
            "defer": 4,
            "hold": 5,
        }
        snapshot = (
            verb == "status"
            and isinstance(result, dict)
            and completed.returncode == 0
            and result.get("home_id") == d["home_id"]
            and "allocations" in result
        )
        if not snapshot and (
            not isinstance(result, dict)
            or (
                6
                if verb == "prepare-launch"
                and fields.get("require_fresh")
                and result.get("status") == "existing"
                else statuses.get(result.get("status"))
            )
            != completed.returncode
        ):
            raise SharedAdmissionControlError("shared_admission_operation_failed")
        receipt = {
            "schema_version": "caplab-shared-control-reply/2",
            "verb": verb,
            "argv": argv,
            # Result text is a foreign encoding (including quota floats and
            # Unicode). Its exact bytes are already in the transport preimage.
            "response_sha256": sha256_hex(completed.stdout),
            "status": result.get("status"),
            "exit_code": completed.returncode,
        }
        _retain(
            self.root,
            "shared-reply-" + sha256_hex(canonical_json(receipt)) + ".json",
            receipt,
        )
        return result

    def control_fault(self, error: SharedAdmissionControlError) -> dict:
        fault = {"status": "hold", "code": str(error), "observed_at": _now()}
        _retain(
            self.root,
            "shared-control-fault-" + sha256_hex(canonical_json(fault)) + ".json",
            fault,
        )
        return fault

    def retire_before_launch(self, completion: Mapping[str, Any]) -> dict | None:
        # Called only after the native one-shot completion has durably closed
        # this right wholly before Popen. Recovery never manufactures completion.
        if completion["launch_attempted_at"] is not None:
            raise LiveExecutionCustodyError("shared_admission_prechild_witness_invalid")
        witness = {
            "completion_sha256": sha256_hex(canonical_json(completion)),
            "clock": _clock_sample(),
        }
        _retain(self.root, "shared-admission-prechild-closure.json", witness)
        return self.reconcile(completion)

    def _retain_list(self, filename: str, body: bytes) -> None:
        path = self.root / filename
        if path.exists():
            if _read(path) != body:
                raise LiveExecutionCustodyError("shared_admission_custody_conflict")
        else:
            _write_exclusive(self.root, filename, body)

    def _owner(self) -> dict:
        if self.record is None:
            raise LiveExecutionCustodyError("shared_admission_allocation_missing")
        return {
            "admission_key": self.record["admission_key_sha256"],
            "holder_id": self.record["holder_id"],
            "fence": self.record["fence"],
        }

    def _prepare(self, containment_argv: list[str]) -> bool:
        plan = self.capture.intent["launch_plan"]
        if (
            sha256_hex(canonical_json(containment_argv))
            != plan["containment_argv_sha256"]
        ):
            raise LiveExecutionCustodyError("shared_admission_containment_mismatch")
        _retain(
            self.root, "shared-admission-containment.json", {"argv": containment_argv}
        )
        d = self.enrollment.document
        intent = self.capture.intent
        self.enrollment.validate_deadline(plan["execution_deadline_at"])
        request = {
            "schema": "quartermaster-shared-admission-request/2",
            "profile_id": self.enrollment.selection.profile["id"],
            "host": self.enrollment.selection.profile["host"],
            "request_id": intent["effect_id"],
            "caller_id": d["caller_id"],
            "route_id": self.enrollment.selection.entry["route_id"],
            "account_id": self.enrollment.selection.entry["account_id"],
            "max_slots": 1,
            "max_launches": 1,
            "home_id": d["home_id"],
            "valid_until": intent["launch_plan"]["execution_deadline_at"],
        }
        _retain(self.root, "shared-admission-request.json", request)
        result = self._call(
            "reserve",
            request=request,
            policy=_read(Path(d["policy_path"])),
            catalog=self.enrollment.projection.release,
            observations=_read(Path(d["observations_path"])),
            holder_id=intent["process_id"],
            namespace="caplab",
        )
        if result["status"] not in {"admitted", "existing"}:
            return False
        self.record = _retain(
            self.root, "shared-admission-allocation.json", result["record"]
        )
        result = self._call(
            "prepare-launch",
            **self._owner(),
            attempt_id=intent["process_id"],
            observations=_read(Path(d["observations_path"])),
            require_fresh=True,
        )
        self.fresh_permit = result["status"] == "prepared"
        path = self.root / "shared-admission-prepare-result.json"
        if path.exists() and result["status"] == "existing":
            return False
        _retain(self.root, path.name, result)
        return self.fresh_permit

    def observe_namespace(self, process, *, deadline: float) -> None:
        self.namespace_witness = namespace_init(process.pid, deadline=deadline)
        if self.namespace_witness is not None:
            _retain(
                self.root,
                "shared-admission-namespace-init.json",
                self.namespace_witness.fact,
            )

    def observe_liveness(self) -> None:
        before = _clock_sample()
        if self.namespace_witness is not None and not self.namespace_witness.dead():
            self.last_alive_at = before["utc"]
            self.last_alive_sample = before

    def close_namespace_observation(self, *, deadline: float | None = None) -> None:
        try:
            # Observation may trail monitor reap. Wait on this same pidfd only,
            # historical routes cap at 50ms and their original native deadline.
            # The prospective readiness route owns a 1s post-monitor observer;
            # it extends no execution/launch authority. Never poll a reused PID.
            wait = (
                0
                if deadline is None
                else (self.post_monitor_observation_ms
                      if self.post_monitor_observation_ms is not None
                      else min(50, max(0, int((deadline - time.monotonic()) * 1000))))
            )
            if self.namespace_witness is not None and self.namespace_witness.dead(wait):
                after = _clock_sample()
                before = self.last_alive_sample
                lower_bound_basis = "observed-live-namespace-init"
                if before is None:
                    try:
                        birth = _read_canonical_document(
                            self.root / "shared-admission-creation.json"
                        )
                    except FileNotFoundError:
                        birth = None
                    # This held init is a child of the positively created outer
                    # process. Its death cannot precede that process's birth.
                    if birth is not None and (
                        birth["schema_version"] == "caplab-shared-creation/2"
                        and birth["outcome"] == "created"
                        and birth["process_id"] == self.capture.intent["process_id"]
                        and birth["pid"] == self.namespace_witness.fact["parent_pid"]
                    ):
                        before = birth["before"]
                        lower_bound_basis = "owned-outer-precreation-clock"
                ended = _interval(before, after, self.capture.intent["process_id"])
                # The held descriptor's boot must match both clock observations.
                if after["boot_id"] != self.namespace_witness.fact["boot_id"]:
                    ended = None
                _retain(
                    self.root,
                    "shared-admission-namespace-closure.json",
                    {
                        "schema_version": "caplab-shared-namespace-closure/2",
                        "process_id": self.capture.intent["process_id"],
                        "namespace_init": self.namespace_witness.fact,
                        "last_alive_at": self.last_alive_at,
                        "lower_bound_basis": lower_bound_basis,
                        "before": before,
                        "after": after,
                        "observed_at": after["utc"],
                        "ended_at": ended,
                        "basis": "owned-namespace-init-pidfd-death",
                    },
                )
        finally:
            if self.namespace_witness is not None:
                self.namespace_witness.close()
                self.namespace_witness = None

    def creation(self, before: dict, after: dict | None, *, pid: int | None) -> None:
        if not self.fresh_permit:
            raise LiveExecutionCustodyError("shared_admission_no_fresh_permit")
        if pid is not None and (type(pid) is not int or pid <= 1):
            raise LiveExecutionCustodyError("shared_admission_child_identity_invalid")
        outcome = "created" if pid is not None else "unresolved"
        created_at = (
            _interval(before, after, self.capture.intent["process_id"])
            if pid is not None
            else None
        )
        material = {
            "schema_version": "caplab-shared-creation/2",
            "process_id": self.capture.intent["process_id"],
            "pid": pid,
            "before": before,
            "after": after,
            "outcome": outcome,
            "created_at": created_at,
            "clock_basis": "trusted-host-utc-measured-bracket",
        }
        _retain(self.root, "shared-admission-creation.json", material)
        try:
            self._record_creation(material)
        except SharedAdmissionControlError as error:
            # Birth is already durable. Finish native capture; recovery retries
            # this same evidence rather than aborting and losing tree custody.
            self.control_fault(error)

    def _record_creation(self, material: dict) -> dict:
        proof = {
            "source_id": self.capture.intent["process_id"],
            "sha256": "sha256:" + sha256_hex(canonical_json(material)),
            "observed_at": (
                (material["after"] or material["before"])["utc"]
                if material["schema_version"] == "caplab-shared-creation/2"
                else material["after"] or material["before"]
            ),
            "created_at": material["created_at"],
            "closed_right_sha256": None,
        }
        return self._call(
            "record-launch",
            **self._owner(),
            attempt_id=self.capture.intent["process_id"],
            outcome=material["outcome"],
            evidence=proof,
        )

    def reconcile(self, completion: Mapping[str, Any] | None) -> dict | None:
        """Reconcile retained facts, never prepare or spawn during recovery."""
        try:
            return self._reconcile(completion)
        except SharedAdmissionControlError as error:
            return self.control_fault(error)

    def _reconcile(self, completion: Mapping[str, Any] | None) -> dict | None:
        allocation = self.root / "shared-admission-allocation.json"
        if not allocation.exists():
            request_path = self.root / "shared-admission-request.json"
            if not request_path.exists():
                return None
            request = _read_canonical_document(request_path)
            snapshot = self._call("status")
            matches = [
                a
                for a in snapshot["allocations"].values()
                if a["request"] == request
                and a["holder_id"] == self.capture.intent["process_id"]
                and a["namespace"] == "caplab"
            ]
            if len(matches) > 1:
                raise LiveExecutionCustodyError("shared_admission_recovery_ambiguous")
            if not matches:
                return {"status": "hold", "code": "admission_commit_unresolved"}
            _retain(self.root, allocation.name, matches[0]["record"])
        self.record = _read_canonical_document(allocation)
        try:
            material = _read_canonical_document(
                self.root / "shared-admission-creation.json"
            )
        except FileNotFoundError:
            if completion is None or completion["launch_attempted_at"] is not None:
                return {"status": "hold", "code": "creation_unresolved"}
            # A native completion produced wholly before Popen closes this one
            # assigned right. No Popen error is in this branch.
            noncreation = self.root / "shared-admission-noncreation.json"
            if noncreation.exists():
                material = _read_canonical_document(noncreation)
                if (
                    material["completion_sha256"]
                    != sha256_hex(canonical_json(completion))
                    or material["process_id"] != self.capture.intent["process_id"]
                ):
                    raise LiveExecutionCustodyError("shared_admission_custody_conflict")
            else:
                prechild = self.root / "shared-admission-prechild-closure.json"
                if not prechild.exists():
                    # A retained authentic pre-Popen completion can be observed now,
                    # including on restart, without pretending its second bucket is
                    # a subsecond observation after a prepared permit.
                    _retain(
                        self.root,
                        prechild.name,
                        {
                            "completion_sha256": sha256_hex(canonical_json(completion)),
                            "clock": _clock_sample(),
                        },
                    )
                witness = _read_canonical_document(prechild)
                if witness["completion_sha256"] != sha256_hex(
                    canonical_json(completion)
                ):
                    raise LiveExecutionCustodyError("shared_admission_custody_conflict")
                material = {
                    "schema_version": "caplab-shared-noncreation/2",
                    "process_id": self.capture.intent["process_id"],
                    "completion_sha256": sha256_hex(canonical_json(completion)),
                    "observed_at": witness["clock"]["utc"],
                }
                _retain(self.root, "shared-admission-noncreation.json", material)
            try:
                permit = _read_canonical_document(
                    self.root / "shared-admission-prepare-result.json"
                )
            except FileNotFoundError:
                recovery_path = self.root / "shared-admission-prepare-recovery.json"
                if recovery_path.exists():
                    permit = _read_canonical_document(recovery_path)
                else:
                    snapshot = self._call("status")
                    entry = snapshot["allocations"][self.record["admission_key_sha256"]]
                    if entry["record"] != self.record:
                        raise LiveExecutionCustodyError(
                            "shared_admission_recovery_ambiguous"
                        )
                    permit = {
                        "status": "recovered",
                        "attempt": entry["attempts"].get(
                            self.capture.intent["process_id"]
                        ),
                    }
                    _retain(self.root, recovery_path.name, permit)
            if (
                permit["status"] in {"prepared", "existing"}
                or permit.get("attempt") is not None
            ):
                proof = {
                    "source_id": self.capture.intent["process_id"],
                    "sha256": "sha256:" + sha256_hex(canonical_json(material)),
                    "observed_at": material["observed_at"],
                    "created_at": None,
                    "closed_right_sha256": "sha256:"
                    + sha256_hex(canonical_json(completion)),
                }
                result = self._call(
                    "record-launch",
                    **self._owner(),
                    attempt_id=self.capture.intent["process_id"],
                    outcome="not_created",
                    evidence=proof,
                )
                if result["status"] not in {"recorded", "existing"}:
                    return result
            return self._settle(material)
        result = self._record_creation(material)
        if result["status"] not in {"recorded", "existing"}:
            return result
        if material["outcome"] != "created" or completion is None:
            return {"status": "hold", "code": "creation_or_time_unresolved"}
        plan = _read_canonical_document(
            self.root / "shared-admission-containment.json"
        )["argv"]
        # Only the pinned live PID namespace + death-on-parent containment is
        # eligible for tree closure. Generic child exit is never a tree oracle.
        if "--" not in plan or not {
            "--unshare-all",
            "--die-with-parent",
            "--new-session",
        } <= set(plan[: plan.index("--")]):
            return {"status": "hold", "code": "tree_containment_unproved"}
        if (
            completion["invocation_state"] != "invoked"
            or completion["exit_code"] is None
        ):
            return {"status": "hold", "code": "tree_closure_unresolved"}
        try:
            quiescence = _read_canonical_document(
                self.root / "shared-admission-namespace-closure.json"
            )
        except FileNotFoundError:
            return {"status": "hold", "code": "namespace_quiescence_unproved"}
        if quiescence["ended_at"] is None:
            return {"status": "hold", "code": "tree_end_time_unresolved"}
        tree = {
            "schema_version": "caplab-shared-tree-closure/1",
            "process_id": self.capture.intent["process_id"],
            "pid": material["pid"],
            "completion": dict(completion),
            "quiescence": quiescence,
            "observed_at": quiescence["observed_at"],
            "containment_plan_sha256": sha256_hex(canonical_json(plan)),
            "basis": "reaped-pinned-outer-plus-owned-namespace-init-pidfd-death",
        }
        tree = _retain(self.root, "shared-admission-tree-closure.json", tree)
        digest = "sha256:" + sha256_hex(canonical_json(tree))
        proof = {
            "source_id": self.capture.intent["process_id"],
            "sha256": digest,
            "observed_at": quiescence["observed_at"],
            "closed_right_sha256": digest,
        }
        result = self._call(
            "close-launch",
            **self._owner(),
            attempt_id=self.capture.intent["process_id"],
            **(
                {"ended_between": quiescence["ended_at"]}
                if isinstance(quiescence["ended_at"], dict)
                else {"ended_at": quiescence["ended_at"]}
            ),
            evidence=proof,
        )
        if result["status"] not in {"closed", "existing"}:
            return result
        return self._settle(tree)

    def _settle(self, material: dict) -> dict:
        digest = "sha256:" + sha256_hex(canonical_json(material))
        proof = {
            "source_id": self.capture.intent["process_id"],
            "sha256": digest,
            "observed_at": material.get("observed_at")
            or material["completion"]["completion_recorded_at"],
            "closed_right_sha256": digest,
            "no_inflight_sha256": digest,
        }
        snapshot = self._call("status")
        entry = snapshot["allocations"][self.record["admission_key_sha256"]]
        if entry["record"] != self.record:
            raise LiveExecutionCustodyError("shared_admission_recovery_ambiguous")
        verb = (
            "reconcile"
            if (entry["terminal"] or {}).get("kind") == "reconciled"
            else "settle"
        )
        result = self._call(verb, **self._owner(), evidence=proof)
        if result.get("status") == "hold" and result.get("code") in {
            "creation_time_unresolved",
            "creation_right_violation",
        }:
            # This branch already proved complete native right/tree closure.
            # An unknown birth or retained validity violation never becomes zero.
            result = self._call("reconcile", **self._owner(), evidence=proof)
        if result.get("status") in {"settled", "reconciled", "existing"}:
            _retain(
                self.root,
                "shared-admission-terminal-result.json",
                {k: v for k, v in result.items() if k != "status"},
            )
        return result


class ProcessAdmission(_AssignedLaunchAdmission):
    """Revbench adapter: only its genuine fresh native capture can acquire rights."""

    def prepare(self, containment_argv: list[str]) -> bool:
        if not isinstance(self.capture, FreshProcessCapture) or self.capture._closed:
            raise LiveExecutionCustodyError("shared_admission_native_right_closed")
        return self._prepare(containment_argv)
