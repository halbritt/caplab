"""Prospective advisory pool launch custody over the existing shared SDK.

Pool assignments own their single-use rights. These are not Revbench captures,
verified public Bindings or authenticated provider identities. No resource
arithmetic or second authoritative resource state lives in this module.
"""
from __future__ import annotations

import json
import hashlib
import math
import os
import secrets
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path

from caplab.runtime.canonical import canonical_json, sha256_hex
from caplab.revbench.custody import (
    LiveExecutionCustodyError, _ensure_owned_directory, _require_secure_parent_directory,
    _write_exclusive, _read_canonical_document,
)
from caplab.revbench.process_tree import SandboxReadiness
from caplab.revbench.shared_admission import (
    SharedAdmissionEnrollment, _AssignedLaunchAdmission, _retain, _read, _now,
)
from caplab.subject_identity import _unwrap_env, validate_native_agent_systems
from caplab.catalog.discovery import load_native_policy
from .run_spec import declaration_digest

SCHEMA = 'caplab-pool-shared-admission/1'


def initialize_pool_domain(out_dir: Path) -> str:
    """Initialize/read native nonrollback custody before writing an enrollment.

    This creates only a local identity, never a ticket, resource allocation or
    execution permission. Keep this owner-controlled directory across restarts.
    """
    out_dir = Path(out_dir).absolute()
    _require_secure_parent_directory(out_dir, 'pool_custody_parent')
    root = _ensure_owned_directory(out_dir, 'shared-launches')
    path = root / 'custody-domain.json'
    if not path.exists():
        body = {'schema_version': 'caplab-pool-custody-domain/1', 'nonce': secrets.token_hex(32)}
        document = {**body, 'custody_domain_id': 'custody-domain-' + sha256_hex(canonical_json(body))}
        try:
            _write_exclusive(root, path.name, canonical_json(document))
        except LiveExecutionCustodyError as error:
            if 'record_exists' not in str(error):
                raise
    document = _read_canonical_document(path)
    if (set(document) != {'schema_version', 'nonce', 'custody_domain_id'}
            or document['schema_version'] != 'caplab-pool-custody-domain/1'
            or not isinstance(document['nonce'], str) or len(document['nonce']) != 64
            or document['custody_domain_id'] != 'custody-domain-' + sha256_hex(canonical_json(
                {k: document[k] for k in ('schema_version', 'nonce')}))):
        raise LiveExecutionCustodyError('pool_custody_domain_invalid')
    return document['custody_domain_id']


class _PoolLaunchRight:
    """Exclusive native assignment claim, published before possible creation."""

    def __init__(self, root: Path, intent: dict, *, recovered: bool = False):
        self.custody_root = root
        self.intent = intent
        self._closed = recovered
        self.completion = None
        if recovered:
            try:
                self.completion = _read_canonical_document(root / 'completion.json')
            except FileNotFoundError:
                pass
        else:
            try:
                root.mkdir(mode=0o700)
            except FileExistsError as error:
                raise LiveExecutionCustodyError('pool_assigned_launch_exists') from error
            parent = os.open(root.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(parent)
            finally:
                os.close(parent)
            _write_exclusive(root, 'intent.json', canonical_json(intent))

    def complete(self, *, attempted_at: str | None, invoked: bool,
                 exit_code: int | None, stdout: bytes, stderr: bytes, error: str | None):
        # Publishing completion consumes this one right. Recovery cannot launch.
        self._closed = True
        _write_exclusive(self.custody_root, 'stdout', stdout)
        _write_exclusive(self.custody_root, 'stderr', stderr)
        self.completion = {
            'schema_version': 'caplab-pool-process-completion/1',
            'process_id': self.intent['process_id'],
            'launch_attempted_at': attempted_at,
            'invocation_state': 'invoked' if invoked else 'not_invoked',
            'exit_code': exit_code, 'completion_recorded_at': _now(),
            'stdout_sha256': sha256_hex(stdout), 'stderr_sha256': sha256_hex(stderr),
            'error': error,
        }
        _write_exclusive(self.custody_root, 'completion.json', canonical_json(self.completion))
        return self.completion


class _PoolProcessAdmission(_AssignedLaunchAdmission):
    def prepare(self, argv: list[str]) -> bool:
        if not isinstance(self.capture, _PoolLaunchRight) or self.capture._closed:
            raise LiveExecutionCustodyError('pool_assigned_launch_closed')
        return self._prepare(argv)


class PoolAdmission:
    """One frozen run enrollment; each explicit assignment is invoked at most once.

    `launch_key` must identify the case/arm/replicate, not a generated retry UUID.
    An interrupted assignment reconciles retained facts and refuses another spawn.
    """

    def __init__(self, enrollment: SharedAdmissionEnrollment, declaration: dict,
                 out_dir: Path, valid_until: str, native_policy_path: Path, *, recovery: bool = False):
        self.enrollment = enrollment
        self.declaration = declaration
        self.valid_until = valid_until
        self.native_policy = load_native_policy(native_policy_path)
        self.root = Path(out_dir).absolute() / 'shared-launches'
        if Path(out_dir).is_symlink() or self.root.is_symlink():
            raise LiveExecutionCustodyError('pool_custody_symlink')
        # Reuse native secure publication primitives, not a resource ledger.
        self.domain_id = initialize_pool_domain(Path(out_dir))
        if self.domain_id != enrollment.document['custody_domain_id']:
            raise LiveExecutionCustodyError('shared_admission_native_identity_mismatch')
        self._validate_declaration()
        enrollment.validate_deadline(valid_until)
        if not recovery:
            self._remaining()
        self.receipt = {
            'schema_version': SCHEMA,
            'enrollment': enrollment.document,
            'declaration_sha256': declaration_digest(declaration),
            'native_policy_sha256': sha256_hex(canonical_json(self.native_policy)),
            'valid_until': valid_until,
            'containment': 'pool-held-pid1-v1',
            'identity_basis': 'configured-profile-and-native-command',
            'authenticated_provider_identity': False,
        }
        _retain(self.root, 'pool-enrollment.json', self.receipt)

    @classmethod
    def read(cls, path: Path, declaration: dict, out_dir: Path, *, recovery: bool = False):
        config = json.loads(_read(Path(path)))
        fields = {'schema_version', 'enrollment_path', 'enrollment_sha256',
                  'declaration_sha256', 'valid_until', 'native_policy_path'}
        if not isinstance(config, dict) or set(config) != fields or config['schema_version'] != SCHEMA:
            raise LiveExecutionCustodyError('pool_enrollment_invalid')
        if declaration_digest(declaration) != config['declaration_sha256']:
            raise LiveExecutionCustodyError('pool_declaration_pin_changed')
        enrollment_path = Path(config['enrollment_path'])
        if not enrollment_path.is_absolute() or sha256_hex(_read(enrollment_path)) != config['enrollment_sha256']:
            raise LiveExecutionCustodyError('pool_enrollment_pin_changed')
        if not (Path(out_dir) / 'shared-launches' / 'pool-enrollment.json').exists() and any(
            (Path(out_dir) / name).exists() for name in ('run-spec.json', 'results.jsonl', 'summary.json')
        ):
            raise LiveExecutionCustodyError('pool_late_enrollment_refused')
        return cls(SharedAdmissionEnrollment.read(enrollment_path), declaration, out_dir, config['valid_until'],
                   Path(config['native_policy_path']), recovery=recovery)

    def _validate_declaration(self):
        selected = self.enrollment.selection
        if hasattr(self, 'receipt') and declaration_digest(self.declaration) != self.receipt['declaration_sha256']:
            raise LiveExecutionCustodyError('pool_declaration_pin_changed')
        if self.declaration.get('id') != selected.entry['key'] or self.declaration.get('status') == 'disabled':
            raise LiveExecutionCustodyError('pool_catalog_declaration_mismatch')
        native = selected.native
        adapter = self.declaration['adapter']
        assignments, command = _unwrap_env(adapter['command'])
        version_assignments, version = _unwrap_env(adapter['version_command'])
        required = native['required_command_tokens']
        if (command[:1] != [native['executable']] or command[1:1 + len(required)] != required
                or version != native['version_command'] or version_assignments != assignments):
            raise LiveExecutionCustodyError('pool_catalog_command_mismatch')
        tuple_id = next((key for key, system in self.native_policy['systems'].items()
                         if all(system.get(k) == native[k] for k in
                                ('model_id', 'native_harness_id', 'effort', 'executable',
                                 'required_command_tokens', 'version_command'))), None)
        validate_native_agent_systems(self.native_policy, {'pool': {
            **native, 'tuple_id': tuple_id, 'command': adapter['command'],
            'version_command': adapter['version_command']}})
        homes = [v.split('=', 1)[1] for v in assignments if v.split('=', 1)[0] in {'CODEX_HOME', 'CLAUDE_CONFIG_DIR', 'HOME'}]
        if homes != ([] if selected.profile['config_home'] is None else [selected.profile['config_home']]):
            raise LiveExecutionCustodyError('pool_catalog_profile_mismatch')
        profile = {'schema_version': 'caplab-pool-configured-profile/1',
                   **{k: selected.profile[k] for k in ('host', 'account_id', 'config_home')},
                   'profile_id': selected.profile['id']}
        if sha256_hex(canonical_json(profile)) != self.enrollment.document['credential_profile_sha256']:
            raise LiveExecutionCustodyError('pool_configured_profile_pin_mismatch')

    def _remaining(self) -> float:
        deadline = datetime.fromisoformat(self.valid_until)
        if deadline.tzinfo is None or deadline.utcoffset().total_seconds() != 0:
            raise LiveExecutionCustodyError('pool_deadline_invalid')
        remaining = (deadline - datetime.now(UTC)).total_seconds()
        if remaining <= 0:
            raise LiveExecutionCustodyError('pool_deadline_expired')
        return remaining

    def run(self, adapter: dict, argv: list[str], *, launch_key: str,
            timeout: float, cwd: str | None, stdin: bytes | None) -> dict:
        self._validate_declaration()
        if initialize_pool_domain(self.root.parent) != self.domain_id:
            raise LiveExecutionCustodyError('pool_custody_domain_changed')
        self.enrollment.check_pins()
        if adapter != self.declaration['adapter'] or not isinstance(launch_key, str) or not launch_key:
            raise LiveExecutionCustodyError('pool_assignment_invalid')
        if not argv or argv[0] != 'bwrap' or '--' not in argv:
            raise LiveExecutionCustodyError('pool_shared_containment_required')
        if type(timeout) not in (int, float) or not math.isfinite(timeout) or timeout <= 0:
            raise LiveExecutionCustodyError('pool_timeout_invalid')
        logical = argv[argv.index('--') + 1:]
        expected = adapter['command']
        extras = 1 if adapter.get('prompt_mode', 'stdin') == 'arg' else 0
        if logical[:len(expected)] != expected or len(logical) != len(expected) + extras:
            raise LiveExecutionCustodyError('pool_native_command_drift')
        deadline = time.monotonic() + min(timeout, self._remaining())
        with SandboxReadiness() as readiness:
            workspace = Path(cwd).resolve() if cwd is not None else None
            if workspace is not None and (workspace == self.root.resolve() or workspace in self.root.resolve().parents):
                raise LiveExecutionCustodyError('pool_custody_in_model_workspace')
            boundary = argv.index('--')
            normalized = ['/usr/bin/bwrap', '--unshare-all', '--share-net', '--new-session',
                          '--block-fd', '{block_fd}', '--info-fd', '{info_fd}',
                          *argv[1:boundary], '--tmpfs', str(self.root), *argv[boundary:]]
            actual = list(normalized)
            actual[actual.index('{block_fd}')] = str(readiness.block_reader)
            actual[actual.index('{info_fd}')] = str(readiness.info_writer)
            plan = {'execution_deadline_at': self.valid_until,
                    'containment_argv_sha256': sha256_hex(canonical_json(normalized))}
            body = {'schema_version': 'caplab-pool-assigned-launch/1',
                    'custody_domain_id': self.domain_id,
                    'binding_id': self.enrollment.document['binding_id'],
                    'assignment': launch_key, 'enrollment_sha256': sha256_hex(canonical_json(self.receipt)),
                    'adapter_sha256': sha256_hex(canonical_json(adapter)),
                    'stdin_sha256': None if stdin is None else sha256_hex(stdin),
                    'bwrap_sha256': sha256_hex(Path('/usr/bin/bwrap').read_bytes()),
                    'launch_plan': plan}
            process_id = 'pool-process-' + sha256_hex(canonical_json(body))
            intent = {**body, 'process_id': process_id, 'effect_id': process_id}
            # The directory key is assignment-based, independent of changed prompt
            # or plan bytes. Drift cannot create a second right for the same slot.
            key = sha256_hex(canonical_json({'domain': self.domain_id, 'assignment': launch_key}))
            right = _PoolLaunchRight(self.root / key, intent)
            control = _PoolProcessAdmission(self.enrollment, right)
            proc = None
            attempted = None
            stdout = stderr = b''
            timed_out = False
            failure = None
            try:
                if not control.prepare(normalized):
                    failure = 'shared admission refused or unavailable'
                elif time.monotonic() >= deadline:
                    failure = 'native launch deadline expired during admission'
                else:
                    before = control.sample_clock()
                    attempted = before['utc']
                    _write_exclusive(right.custody_root, 'possible-creation.json', canonical_json(before))
                    try:
                        proc = subprocess.Popen(actual, stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
                                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                                cwd=cwd, pass_fds=readiness.pass_fds)
                    except BaseException:
                        control.creation(before, None, pid=None)
                        raise
                    after = control.sample_clock()
                    readiness.child_started()
                    control.creation(before, after, pid=proc.pid)
                    control.adopt_namespace(readiness.observe(proc.pid, deadline=deadline), post_monitor_timeout_ms=1000)
                    control.observe_liveness()
                    if time.monotonic() >= deadline or self._remaining() <= 0:
                        raise LiveExecutionCustodyError('pool_deadline_expired_before_release')
                    readiness.release()
                    try:
                        stdout, stderr = proc.communicate(stdin, timeout=max(0, deadline - time.monotonic()))
                    except subprocess.TimeoutExpired:
                        timed_out = True
                        proc.kill()
                        stdout, stderr = proc.communicate(timeout=1)
            except BaseException as error:
                failure = type(error).__name__ + ':' + str(error)
                # Closing a block writer releases bwrap. Reap monitor first; no
                # swallowed kill/wait error can become positive tree completion.
                if proc is not None:
                    if proc.poll() is None:
                        proc.kill()
                    proc.wait(timeout=1)
                    # A blocked PID1 may still own the pipe until context closure.
                    # Do not wait on its EOF or manufacture complete output.
                    for stream in (proc.stdin, proc.stdout, proc.stderr):
                        if stream is not None:
                            stream.close()
                right.complete(attempted_at=attempted, invoked=proc is not None,
                               exit_code=None if proc is None else proc.returncode,
                               stdout=stdout, stderr=stderr, error=failure)
                control.reconcile(right.completion)
                readiness.abort()
                control.close_namespace_observation(deadline=deadline)
                raise
            completion = right.complete(attempted_at=attempted, invoked=proc is not None,
                                        exit_code=None if proc is None else proc.returncode,
                                        stdout=stdout, stderr=stderr, error=failure)
            control.close_namespace_observation(deadline=deadline)
            shared = ({'status': 'refuse', 'code': 'not_admitted'} if control.record is None
                      else control.retire_before_launch(completion) if attempted is None
                      else control.reconcile(completion))
            return {'stdout': stdout, 'exit_code': completion['exit_code'],
                    'timed_out': timed_out, 'error': failure, 'shared_admission': shared,
                    'custody_path': str(right.custody_root)}

    def reconcile(self) -> list[dict | None]:
        """No launch, reserve, prepare or numeric PID inspection during restart."""
        results = []
        for root in sorted(self.root.iterdir()):
            if root.is_symlink():
                raise LiveExecutionCustodyError('pool_custody_symlink')
            if not root.is_dir():
                continue
            intent = _read_canonical_document(root / 'intent.json')
            if (intent['schema_version'] != 'caplab-pool-assigned-launch/1'
                    or intent['custody_domain_id'] != self.domain_id
                    or intent['enrollment_sha256'] != sha256_hex(canonical_json(self.receipt))):
                raise LiveExecutionCustodyError('pool_retained_identity_mismatch')
            body = {k: v for k, v in intent.items() if k not in {'effect_id', 'process_id'}}
            expected_id = 'pool-process-' + sha256_hex(canonical_json(body))
            expected_root = sha256_hex(canonical_json({'domain': self.domain_id, 'assignment': intent['assignment']}))
            if intent['process_id'] != expected_id or intent['effect_id'] != expected_id or root.name != expected_root:
                raise LiveExecutionCustodyError('pool_retained_intent_changed')
            right = _PoolLaunchRight(root, intent, recovered=True)
            if right.completion is not None:
                completion = right.completion
                if (completion['schema_version'] != 'caplab-pool-process-completion/1'
                        or completion['process_id'] != expected_id
                        or completion['stdout_sha256'] != _stream_digest(root / 'stdout')
                        or completion['stderr_sha256'] != _stream_digest(root / 'stderr')):
                    raise LiveExecutionCustodyError('pool_retained_completion_changed')
            results.append(_PoolProcessAdmission(self.enrollment, right).reconcile(right.completion))
        return results


def _stream_digest(path: Path) -> str:
    # Native outputs retain their existing size contract. Recovery hashes them
    # incrementally rather than inheriting the control-plane JSON byte limit.
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(descriptor, 'rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()
