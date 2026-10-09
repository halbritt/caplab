"""Native retrieval assignment custody; the SDK alone owns resource accounting.

An operator-pinned arm/account mapping is a declared enforced domain, not
provider authentication, a native-agent Binding or qualification evidence.
"""
from __future__ import annotations

import json
import os
import secrets
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from caplab.runtime.canonical import canonical_json, sha256_hex
from caplab.revbench.custody import (LiveExecutionCustodyError, _ensure_owned_directory,
    _require_secure_parent_directory, _write_exclusive, _read_canonical_document)
from caplab.revbench.shared_admission import (SharedAdmissionEnrollment,
    _AssignedLaunchAdmission, _retain, _read, _now)
from caplab.revbench.process_tree import SandboxReadiness, preserve_launch_error
from caplab.revbench.codex import _terminate_process_group
from . import contracts

SCHEMA = 'caplab-retrieval-shared-admission/1'


def initialize_domain(parent: Path) -> str:
    """Create/read a persistent native identity; reserves nothing and grants no launch."""
    parent = Path(parent).absolute()
    _require_secure_parent_directory(parent, 'retrieval_custody_parent')
    root = _ensure_owned_directory(parent, 'shared-launches')
    path = root / 'custody-domain.json'
    if not path.exists():
        body = {'schema_version': 'caplab-retrieval-custody-domain/1', 'nonce': secrets.token_hex(32)}
        try:
            _write_exclusive(root, path.name, canonical_json({**body,
                'custody_domain_id': 'custody-domain-' + sha256_hex(canonical_json(body))}))
        except LiveExecutionCustodyError as error:
            if 'record_exists' not in str(error):
                raise
    document = _read_canonical_document(path)
    if (set(document) != {'schema_version', 'nonce', 'custody_domain_id'}
        or document['schema_version'] != 'caplab-retrieval-custody-domain/1'
        or not isinstance(document['nonce'], str) or len(document['nonce']) != 64
        or document['custody_domain_id'] != 'custody-domain-' + sha256_hex(canonical_json(
            {k: document[k] for k in ('schema_version', 'nonce')}))):
        raise LiveExecutionCustodyError('retrieval_custody_domain_invalid')
    return document['custody_domain_id']


def read_enrollment(path: Path, spec: dict) -> dict:
    """Load complete opt-in command-arm coverage; never silently omit an arm."""
    config = json.loads(_read(Path(path)))
    if (not isinstance(config, dict) or set(config) != {'schema_version', 'custody_root', 'valid_until', 'spec_sha256', 'arms'}
        or config['schema_version'] != SCHEMA or config['spec_sha256'] != contracts.spec_digest(spec)
        or not isinstance(config['arms'], list) or not Path(config['custody_root']).is_absolute()):
        raise LiveExecutionCustodyError('retrieval_enrollment_invalid')
    expected = {a['id'] for a in spec['arms'] if a['adapter'] == 'command'}
    if len(expected) != len(spec['arms']):
        raise LiveExecutionCustodyError('retrieval_noncommand_coverage_unavailable')
    controllers = {}
    for row in config['arms']:
        if (not isinstance(row, dict) or set(row) != {'arm_id', 'enrollment_path', 'enrollment_sha256'}
            or row['arm_id'] not in expected or row['arm_id'] in controllers):
            raise LiveExecutionCustodyError('retrieval_arm_mapping_invalid')
        p = Path(row['enrollment_path'])
        if not p.is_absolute() or sha256_hex(_read(p)) != row['enrollment_sha256']:
            raise LiveExecutionCustodyError('retrieval_enrollment_pin_changed')
        controllers[row['arm_id']] = RetrievalAdmission(SharedAdmissionEnrollment.read(p), spec, row['arm_id'],
                                                       Path(config['custody_root']), config['valid_until'])
    if set(controllers) != expected:
        raise LiveExecutionCustodyError('retrieval_arm_mapping_incomplete')
    return controllers


class _RetrievalRight:
    def __init__(self, root: Path, intent: dict, *, recovered=False):
        self.custody_root, self.intent = root, intent
        self._closed = recovered
        self.completion = None
        if recovered:
            try:
                self.completion = _read_canonical_document(root / 'completion.json')
            except FileNotFoundError:
                pass
        else:
            root.mkdir(mode=0o700)  # exclusive assignment claim across handles/processes
            descriptor = os.open(root.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
            _write_exclusive(root, 'intent.json', canonical_json(intent))

    def complete(self, done, *, attempted_at, invoked, error=None, cleanup_errors=None):
        self._closed = True
        _write_exclusive(self.custody_root, 'stdout', done.stdout)
        _write_exclusive(self.custody_root, 'stderr', done.stderr)
        document = {'schema_version': 'caplab-retrieval-process-completion/1',
            'process_id': self.intent['process_id'], 'launch_attempted_at': attempted_at,
            'invocation_state': 'invoked' if invoked else 'not_invoked',
            'exit_code': done.returncode, 'completion_recorded_at': _now(),
            'stdout_sha256': sha256_hex(done.stdout), 'stderr_sha256': sha256_hex(done.stderr),
            'timed_out': done.timed_out, 'truncated': done.truncated, 'elapsed_ns': done.elapsed_ns,
            'outputs_complete': error is None, 'error': error}
        if cleanup_errors:
            document['cleanup_errors'] = list(cleanup_errors)
        self.completion = _retain(self.custody_root, 'completion.json', document)
        return self.completion


class _RetrievalControl(_AssignedLaunchAdmission):
    def prepare(self, argv):
        if not isinstance(self.capture, _RetrievalRight) or self.capture._closed:
            raise LiveExecutionCustodyError('retrieval_assigned_launch_closed')
        return self._prepare(argv)


class RetrievalAdmission:
    """One frozen command arm with assignment-keyed rights; replay cannot launch."""
    def __init__(self, enrollment, spec, arm_id, parent, valid_until):
        self.enrollment = enrollment
        self.spec = json.loads(contracts.canonical_json(spec))
        self.arm = arm_id
        self.domain_id = initialize_domain(parent)
        if self.domain_id != enrollment.document['custody_domain_id']:
            raise LiveExecutionCustodyError('retrieval_custody_domain_mismatch')
        self.valid_until = valid_until
        deadline = datetime.fromisoformat(valid_until)
        if deadline.tzinfo is None or deadline.utcoffset().total_seconds() != 0:
            raise LiveExecutionCustodyError('retrieval_deadline_invalid')
        enrollment.validate_deadline(valid_until)
        self.root = _ensure_owned_directory(Path(parent) / 'shared-launches', 'assignments')
        selected = enrollment.selection
        profile = {'schema_version': 'caplab-retrieval-declared-profile/1',
            'profile_id': selected.profile['id'],
            **{k: selected.profile[k] for k in ('host', 'account_id', 'config_home')}}
        if sha256_hex(canonical_json(profile)) != enrollment.document['credential_profile_sha256']:
            raise LiveExecutionCustodyError('retrieval_declared_profile_pin_mismatch')
        self.receipt = {'schema_version': 'caplab-retrieval-arm-enrollment/1',
            'spec_sha256': contracts.spec_digest(self.spec), 'arm_id': self.arm,
            'enrollment': enrollment.document, 'declared_profile': profile,
            'valid_until': valid_until, 'identity_basis': 'operator-declared-account-domain',
            'authenticated_provider_identity': False, 'containment': 'retrieval-held-pid1-explicit-exec-gate-v1'}
        self.receipt_sha = sha256_hex(canonical_json(self.receipt))
        _retain(Path(parent) / 'shared-launches', 'arm-' + self.receipt_sha + '.json', self.receipt)
        self.command_pin = None

    def pin(self, command_pin):
        self.enrollment.check_pins()
        pin = json.loads(contracts.canonical_json(command_pin))
        if self.command_pin is not None and pin != self.command_pin:
            raise LiveExecutionCustodyError('retrieval_command_pin_changed')
        self.command_pin = pin
        return self.receipt

    def describe(self):
        selected = self.enrollment.selection
        account = next(a for a in self.enrollment.projection.release['catalog']['accounts']
                       if a['id'] == selected.entry['account_id'])
        return {**self.receipt, 'declared_account_id': account['id'], 'pool_ids': account['quota_pool_ids'],
                'covered_launch_path': 'enrolled retrieval command arm per sealed assignment',
                'residual_scope': 'Cairn helpers/database, other producers and uninstrumented clients remain unenrolled.'}

    def _identity(self, assignment):
        roster = {a['assignment_id'] for a in contracts.assignments(self.spec) if a['arm'] == self.arm}
        if assignment not in roster:
            raise LiveExecutionCustodyError('retrieval_assignment_unplanned')
        return sha256_hex(canonical_json({'domain': self.domain_id,
            'experiment_id': self.spec['experiment_id'], 'assignment': assignment}))

    def run(self, argv, *, assignment, stdin, cwd, env, timeout):
        from .runner import Completed, _capture_process, MAX_OUTPUT_BYTES
        start = time.monotonic_ns()
        deadline = time.monotonic() + timeout
        self.enrollment.check_pins()
        if self.command_pin is None or argv != self.command_pin['argv']:
            raise LiveExecutionCustodyError('retrieval_command_unpinned')
        if cwd == self.root or self.root in cwd.parents or cwd in self.root.parents:
            raise LiveExecutionCustodyError('retrieval_custody_in_command_workspace')
        key = self._identity(assignment)
        with SandboxReadiness() as readiness:
            normalized = ['/usr/bin/bwrap', '--unshare-all', '--share-net', '--new-session', '--die-with-parent',
                '--block-fd', '{block_fd}', '--info-fd', '{info_fd}', '--ro-bind', '/', '/',
                '--dev', '/dev', '--proc', '/proc', '--bind', str(cwd), str(cwd),
                '--tmpfs', str(self.root.parent), '--tmpfs', self.enrollment.document['home'], '--',
                sys.executable, '-I', '-S', str(Path(__file__).with_name('exec_gate.py')), *argv]
            # Scratch paths vary by call. They are native temporary directories,
            # not assignment identity; seal their symbolic representation.
            sealed = [part.replace(str(cwd), '{scratch}') for part in normalized]
            body = {'schema_version': 'caplab-retrieval-assigned-launch/1',
                'custody_domain_id': self.domain_id, 'experiment_id': self.spec['experiment_id'],
                'assignment': assignment, 'spec_sha256': contracts.spec_digest(self.spec),
                'arm_id': self.arm, 'enrollment_sha256': self.receipt_sha, 'command_pin': self.command_pin,
                'stdin_sha256': sha256_hex(stdin),
                'bwrap_sha256': sha256_hex(Path('/usr/bin/bwrap').read_bytes()),
                'exec_gate_sha256': sha256_hex(Path(__file__).with_name('exec_gate.py').read_bytes()),
                'gate_interpreter_sha256': sha256_hex(Path(sys.executable).read_bytes()),
                'launch_plan': {'execution_deadline_at': self.valid_until,
                                'containment_argv_sha256': sha256_hex(canonical_json(sealed))}}
            pid = 'retrieval-process-' + sha256_hex(canonical_json(body))
            intent = {**body, 'process_id': pid, 'effect_id': pid}
            path = self.root / key
            if path.exists():
                return self._recover(path, intent)
            remaining = (datetime.fromisoformat(self.valid_until) - datetime.now(UTC)).total_seconds()
            if remaining <= 0:
                raise LiveExecutionCustodyError('retrieval_deadline_expired')
            deadline = min(deadline, time.monotonic() + remaining)
            try:
                right = _RetrievalRight(path, intent)
            except FileExistsError:
                return self._recover(path, intent)
            control = _RetrievalControl(self.enrollment, right)
            proc = None
            attempted = None
            done = Completed(None, b'', b'', False, False, 0)
            try:
                admitted = control.prepare(sealed)
                if admitted and time.monotonic() < deadline:
                    before = control.sample_clock()
                    attempted = before['utc']
                    _write_exclusive(path, 'possible-creation.json', canonical_json(before))
                    actual = [str(readiness.block_reader) if p == '{block_fd}' else
                              str(readiness.info_writer) if p == '{info_fd}' else p for p in normalized]
                    try:
                        proc = subprocess.Popen(actual, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, cwd=cwd, env=env, pass_fds=readiness.pass_fds, start_new_session=True)
                    except BaseException as error:
                        with preserve_launch_error(error, 'retrieval_creation_uncertainty'):
                            control.creation(before, None, pid=None)
                        raise
                    readiness.child_started()
                    control.creation(before, control.sample_clock(), pid=proc.pid)
                    control.adopt_namespace(readiness.observe(proc.pid, deadline=deadline), post_monitor_timeout_ms=1000)
                    control.observe_liveness()
                    if time.monotonic() >= deadline:
                        raise LiveExecutionCustodyError('retrieval_deadline_expired_before_release')
                    readiness.release()
                    done = _capture_process(proc, stdin=b'\x01' + stdin, timeout=max(0, deadline - time.monotonic()),
                                            limit=MAX_OUTPUT_BYTES, start=start)
                control.close_namespace_observation(deadline=deadline)
                completion = right.complete(done, attempted_at=attempted, invoked=proc is not None)
                result = (control.retire_before_launch(completion) if attempted is None and control.record is not None
                          else control.reconcile(completion))
                return done, {'result': result, 'custody_path': str(path), 'recovery_basis': 'fresh-assignment'}
            except BaseException as error:
                if proc is not None:
                    with preserve_launch_error(error, 'retrieval_group_abort'):
                        _terminate_process_group(proc, force=True)
                with preserve_launch_error(error, 'retrieval_readiness_abort'):
                    readiness.abort()
                if proc is not None:
                    with preserve_launch_error(error, 'retrieval_monitor_reap'):
                        proc.wait(timeout=1)
                    for stream in (proc.stdin, proc.stdout, proc.stderr):
                        with preserve_launch_error(error, 'retrieval_stream_close'):
                            stream.close()
                with preserve_launch_error(error, 'retrieval_namespace_close'):
                    control.close_namespace_observation(deadline=deadline)
                if right.completion is None:
                    with preserve_launch_error(error, 'retrieval_completion_publish'):
                        right.complete(Completed(None if proc is None else proc.returncode, done.stdout, done.stderr,
                                               done.timed_out, done.truncated, time.monotonic_ns() - start),
                                       attempted_at=attempted, invoked=proc is not None,
                                       error=type(error).__name__ + ':' + str(error),
                                       cleanup_errors=getattr(error, '__notes__', []))
                with preserve_launch_error(error, 'retrieval_reconcile'):
                    control.reconcile(right.completion)
                raise

    def _retained(self, path, intent=None):
        if path.is_symlink():
            raise LiveExecutionCustodyError('retrieval_custody_symlink')
        d = _read_canonical_document(path / 'intent.json')
        body = {k: v for k, v in d.items() if k not in {'process_id', 'effect_id'}}
        pid = 'retrieval-process-' + sha256_hex(canonical_json(body))
        if (d['schema_version'] != 'caplab-retrieval-assigned-launch/1'
            or d['process_id'] != pid or d['effect_id'] != pid
            or d['enrollment_sha256'] != self.receipt_sha or d['arm_id'] != self.arm
            or self._identity(d['assignment']) != path.name or (intent is not None and d != intent)):
            raise LiveExecutionCustodyError('retrieval_retained_intent_changed')
        right = _RetrievalRight(path, d, recovered=True)
        if right.completion is not None:
            c = right.completion
            if (c['schema_version'] != 'caplab-retrieval-process-completion/1'
                or c['process_id'] != pid or type(c['elapsed_ns']) is not int or c['elapsed_ns'] < 0
                or type(c['outputs_complete']) is not bool
                or type(c['timed_out']) is not bool or type(c['truncated']) is not bool
                or (c['exit_code'] is not None and type(c['exit_code']) is not int)):
                raise LiveExecutionCustodyError('retrieval_retained_completion_changed')
            from .runner import MAX_OUTPUT_BYTES
            for name in ('stdout', 'stderr'):
                fd = os.open(path / name, os.O_RDONLY | os.O_NOFOLLOW)
                with os.fdopen(fd, 'rb') as stream:
                    data = stream.read(MAX_OUTPUT_BYTES + 1)
                if len(data) > MAX_OUTPUT_BYTES or sha256_hex(data) != c[name + '_sha256']:
                    raise LiveExecutionCustodyError('retrieval_retained_output_changed')
        return right

    def _recover(self, path, intent):
        from .runner import AdapterError, Completed
        try:
            right = self._retained(path, intent)
        except FileNotFoundError:
            raise AdapterError('shared_admission_unresolved', 'assigned custody is incomplete; no retry') from None
        result = _RetrievalControl(self.enrollment, right).reconcile(right.completion)
        if right.completion is None or not right.completion['outputs_complete']:
            raise AdapterError('shared_admission_unresolved', 'assigned outcome unavailable; no retry')
        c = right.completion
        if c['schema_version'] != 'caplab-retrieval-process-completion/1' or c['process_id'] != right.intent['process_id']:
            raise LiveExecutionCustodyError('retrieval_retained_completion_changed')
        streams = []
        for name in ('stdout', 'stderr'):
            fd = os.open(path / name, os.O_RDONLY | os.O_NOFOLLOW)
            with os.fdopen(fd, 'rb') as stream:
                from .runner import MAX_OUTPUT_BYTES
                data = stream.read(MAX_OUTPUT_BYTES + 1)
            if sha256_hex(data) != c[name + '_sha256']:
                raise LiveExecutionCustodyError('retrieval_retained_output_changed')
            streams.append(data)
        return Completed(c['exit_code'], *streams, c['timed_out'], c['truncated'], c['elapsed_ns']), {
            'result': result, 'custody_path': str(path), 'recovery_basis': 'retained-completion'}

    def reconcile(self):
        results = []
        for path in sorted(self.root.iterdir()):
            if not path.is_dir():
                raise LiveExecutionCustodyError('retrieval_unexpected_custody_entry')
            try:
                raw = _read_canonical_document(path / 'intent.json')
            except FileNotFoundError:
                results.append({'status': 'hold', 'code': 'native_custody_incomplete'})
                continue
            if raw['arm_id'] != self.arm:
                continue
            right = self._retained(path)
            results.append(_RetrievalControl(self.enrollment, right).reconcile(right.completion))
        return results
