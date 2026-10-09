"""Opt-in native calibration launch custody; SDK accounting remains external.

Assignments identify helpers/trials, never native model qualification. The
original bwrap administration is retained around an explicit-byte exec gate.
"""
from __future__ import annotations

import json
import math
import copy
import os
import secrets
import subprocess
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

from caplab.runtime.canonical import canonical_json, sha256_hex
from caplab.revbench.custody import (LiveExecutionCustodyError, _ensure_owned_directory,
    _require_secure_parent_directory, _write_exclusive, _read_canonical_document)
from caplab.revbench.shared_admission import (SharedAdmissionEnrollment,
    _AssignedLaunchAdmission, _retain, _read, _now)
from caplab.revbench.process_tree import SandboxReadiness, preserve_launch_error
from caplab.revbench.codex import _terminate_process_group

SCHEMA = 'caplab-native-shared-admission/1'


def initialize_domain(parent: Path) -> str:
    """Create/read native custody identity; no SDK reservation or launch right."""
    parent = Path(parent).absolute()
    _require_secure_parent_directory(parent, 'native_custody_parent')
    root = _ensure_owned_directory(parent, 'shared-launches')
    path = root / 'custody-domain.json'
    if not path.exists():
        body = {'schema_version': 'caplab-native-custody-domain/1', 'nonce': secrets.token_hex(32)}
        try:
            _write_exclusive(root, path.name, canonical_json({**body,
                'custody_domain_id': 'custody-domain-' + sha256_hex(canonical_json(body))}))
        except LiveExecutionCustodyError as error:
            if 'record_exists' not in str(error):
                raise
    document = _read_canonical_document(path)
    body = {k: document[k] for k in ('schema_version', 'nonce')}
    if (set(document) != {'schema_version', 'nonce', 'custody_domain_id'}
        or body['schema_version'] != 'caplab-native-custody-domain/1'
        or not isinstance(body['nonce'], str) or len(body['nonce']) != 64
        or document['custody_domain_id'] != 'custody-domain-' + sha256_hex(canonical_json(body))):
        raise LiveExecutionCustodyError('native_custody_domain_invalid')
    return document['custody_domain_id']


def platform_version_probe(root):
    """One platform helper inside an owned namespace, with no credential mount."""
    return ['/usr/bin/bwrap', '--unshare-all', '--new-session', '--die-with-parent',
        '--ro-bind', '/usr', '/usr', '--ro-bind', '/bin', '/bin', '--ro-bind', '/lib', '/lib',
        '--ro-bind', '/lib64', '/lib64', '--proc', '/proc', '--dev', '/dev', '--tmpfs', '/tmp',
        '--bind', str(root), '/work', '--chdir', '/work', '--', '/usr/bin/bwrap', '--version']


class _NativeRight:
    def __init__(self, root, intent, *, recovered=False):
        self.custody_root, self.intent = root, intent
        self._closed = recovered
        self.completion = None
        if recovered:
            try:
                self.completion = _read_canonical_document(root / 'completion.json')
            except FileNotFoundError:
                pass
        else:
            root.mkdir(mode=0o700)
            fd = os.open(root.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
            _write_exclusive(root, 'intent.json', canonical_json(intent))

    def complete(self, *, attempted_at, process, stdout, stderr, timed_out, started, error=None):
        self._closed = True
        _write_exclusive(self.custody_root, 'stdout', stdout)
        _write_exclusive(self.custody_root, 'stderr', stderr)
        self.completion = _retain(self.custody_root, 'completion.json', {
            'schema_version': 'caplab-native-process-completion/1',
            'process_id': self.intent['process_id'], 'launch_attempted_at': attempted_at,
            'invocation_state': 'invoked' if process is not None else 'not_invoked',
            'exit_code': None if process is None else process.returncode,
            'completion_recorded_at': _now(), 'stdout_sha256': sha256_hex(stdout),
            'stderr_sha256': sha256_hex(stderr), 'timed_out': timed_out,
            'outputs_complete': error is None, 'started_at': started,
            'finished_at': datetime.now(UTC).isoformat(), 'error': error})
        return self.completion


class _NativeControl(_AssignedLaunchAdmission):
    def prepare(self, argv):
        if not isinstance(self.capture, _NativeRight) or self.capture._closed:
            raise LiveExecutionCustodyError('native_assigned_launch_closed')
        return self._prepare(argv)


class NativeCalibrationAdmission:
    """Complete subject/helper coverage of one pinned native campaign.

    run() has subprocess.run's captured-byte/timeout contract. Constructor and
    SDK failures propagate; they are not fabricated native measurement results.
    All assignments have a stable caller name, independent of command bytes.
    """
    @classmethod
    def read(cls, path, manifest, *, family):
        raw = _read(Path(path))
        d = json.loads(raw)
        if (not isinstance(d, dict) or set(d) != {'schema_version', 'family', 'manifest_sha256', 'subjects'}
            or d['schema_version'] != SCHEMA or d['family'] != family
            or family not in {'preference', 'review-dissent'}
            or d['manifest_sha256'] != manifest['manifest_sha256']
            or not isinstance(d['subjects'], list)):
            raise LiveExecutionCustodyError('native_enrollment_invalid')
        self = cls()
        self.manifest, self.family = copy.deepcopy(manifest), family
        if manifest.get('_verified_manifest_sha256') != manifest['manifest_sha256']:
            raise LiveExecutionCustodyError('native_manifest_not_verified')
        self.config_pin = sha256_hex(raw)
        self.parent = Path(manifest['storage']['raw_custody_root']).absolute()
        self.domain = initialize_domain(self.parent)
        self.root = _ensure_owned_directory(self.parent / 'shared-launches', 'assignments')
        self.enrollments = {}
        home = None
        self.receipts = {}
        for row in d['subjects']:
            if (not isinstance(row, dict) or set(row) != {'subject_id', 'native_config_home', 'enrollment_path', 'enrollment_sha256'}
                or row['subject_id'] not in {'fable', 'gpt', 'platform'}
                or row['subject_id'] in self.enrollments
                or (row['native_config_home'] is not None and
                    (not isinstance(row['native_config_home'], str) or not Path(row['native_config_home']).is_absolute()))):
                raise LiveExecutionCustodyError('native_subject_mapping_invalid')
            p = Path(row['enrollment_path'])
            if not p.is_absolute() or sha256_hex(_read(p)) != row['enrollment_sha256']:
                raise LiveExecutionCustodyError('native_enrollment_pin_changed')
            e = SharedAdmissionEnrollment.read(p)
            if 'sdk_source_tree_sha256' not in e.document:
                raise LiveExecutionCustodyError('native_sdk_source_pin_required')
            if e.document['custody_domain_id'] != self.domain or e.document['caller_id'] != 'caplab':
                raise LiveExecutionCustodyError('native_custody_domain_mismatch')
            joined = tuple(e.document[k] for k in ('home', 'home_id', 'policy_sha256', 'release_sha256', 'sdk_source_tree_sha256'))
            if home is not None and home != joined:
                raise LiveExecutionCustodyError('native_multiple_admission_homes')
            home = joined
            profile = {'schema_version': 'caplab-native-declared-profile/1',
                'profile_id': e.selection.profile['id'],
                **{k: e.selection.profile[k] for k in ('host', 'account_id', 'config_home')},
                'native_config_home': row['native_config_home']}
            if sha256_hex(canonical_json(profile)) != e.document['credential_profile_sha256']:
                raise LiveExecutionCustodyError('native_declared_profile_pin_mismatch')
            subject = row['subject_id']
            if subject != 'platform' and e.document['binding_id'] != manifest['_instrument']['agent_systems'][subject]['tuple_id']:
                raise LiveExecutionCustodyError('native_subject_tuple_mismatch')
            self.enrollments[subject] = e
            self.receipts[subject] = {'enrollment': e.document, 'declared_profile': profile}
        if set(self.enrollments) != {'fable', 'gpt', 'platform'}:
            raise LiveExecutionCustodyError('native_subject_mapping_incomplete')
        self.receipt = {'schema_version': SCHEMA, 'family': family,
            'manifest_sha256': manifest['manifest_sha256'], 'config_file_sha256': self.config_pin,
            'subjects': self.receipts, 'identity_basis': 'operator-declared-account-domain',
            'authenticated_provider_identity': False,
            'containment': 'native-task-namespace-explicit-exec-gate-v1'}
        from caplab.revbench import custody, shared_admission, process_tree, codex
        from caplab.runtime import canonical
        from caplab.retrieval import exec_gate
        self.receipt['runtime_sources'] = {m.__name__: sha256_hex(Path(m.__file__).read_bytes())
            for m in (custody, shared_admission, process_tree, codex, canonical, exec_gate)}
        self.receipt['runtime_sources'][__name__] = sha256_hex(Path(__file__).read_bytes())
        self.receipt_sha = sha256_hex(canonical_json(self.receipt))
        _retain(self.parent / 'shared-launches', 'enrollment-' + self.receipt_sha + '.json', self.receipt)
        return self

    def validate_native_homes(self, homes):
        """The producer supplies actual native config paths, never credential bytes."""
        if set(homes) != set(self.receipts) or any(
            homes[s] != self.receipts[s]['declared_profile']['native_config_home'] for s in homes):
            raise LiveExecutionCustodyError('native_config_home_mapping_mismatch')

    def describe(self):
        return {**copy.deepcopy(self.receipt), 'covered_launches': ['fable-version', 'gpt-version', 'platform-version',
            'fable-auth', 'gpt-auth', 'native-trial'],
            'residual_scope': 'Other producers, historical campaigns and unenrolled clients remain unenrolled.'}

    def completion_for(self, subject, assignment):
        return self._retained(self.root / self._key(subject, assignment)).completion

    def _key(self, subject, assignment):
        return sha256_hex(canonical_json({'domain': self.domain, 'family': self.family,
            'campaign_id': self.manifest['campaign_id'], 'subject': subject, 'assignment': assignment}))

    def _argv(self, command, cwd):
        from caplab.retrieval import exec_gate
        gate = Path(exec_gate.__file__)
        if (not isinstance(command, list) or not command or command[0] != '/usr/bin/bwrap'
            or '--' not in command or '--unshare-all' not in command or '--die-with-parent' not in command
            or '--block-fd' in command or '--info-fd' in command):
            raise LiveExecutionCustodyError('native_containment_not_supported')
        cut = command.index('--')
        destination = getattr(self, 'gate_destination', '/caplab-launch-gate.py')
        argv = command[:cut] + ['--block-fd', '{block_fd}', '--info-fd', '{info_fd}',
            '--ro-bind', str(gate), destination, '--',
            '/usr/bin/python3', '-I', '-S', destination] + command[cut+1:]
        return argv, [part.replace(str(cwd), '{workspace}') for part in argv], gate

    def run(self, command, *, cwd, subject, assignment, timeout, env=None, native_launch_sha256=None, input=None):
        if subject not in self.enrollments or not isinstance(assignment, str) or not assignment:
            raise LiveExecutionCustodyError('native_assignment_invalid')
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or timeout <= 0:
            raise LiveExecutionCustodyError('native_timeout_invalid')
        if input is not None and not isinstance(input, bytes):
            raise LiveExecutionCustodyError('native_input_must_be_bytes')
        env = {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8'} if env is None else dict(env)
        if set(env) != {'PATH', 'LANG'} or any(not isinstance(v, str) for v in env.values()):
            raise LiveExecutionCustodyError('native_launcher_environment_invalid')
        cwd = Path(cwd).resolve(strict=True)
        e = self.enrollments[subject]
        e.check_pins()
        argv, sealed, gate = self._argv(command, cwd)
        body = {'schema_version': 'caplab-native-assigned-launch/1', 'family': self.family,
            'custody_domain_id': self.domain, 'campaign_id': self.manifest['campaign_id'],
            'manifest_sha256': self.manifest['manifest_sha256'], 'subject': subject,
            'assignment': assignment, 'enrollment_sha256': self.receipt_sha,
            'native_launch_sha256': native_launch_sha256,
            'argv': sealed, 'environment': dict(env or {}),
            'bwrap_sha256': sha256_hex(Path('/usr/bin/bwrap').read_bytes()),
            'exec_gate_sha256': sha256_hex(gate.read_bytes()),
            'gate_interpreter_sha256': sha256_hex(Path('/usr/bin/python3').read_bytes())}
        if input is not None:
            body['stdin_sha256'] = sha256_hex(input)
        path = self.root / self._key(subject, assignment)
        if path.exists():
            return self._recover(path, body, command, timeout)
        now = datetime.now(UTC)
        until = min(datetime.fromisoformat(self.manifest['expires_at']).astimezone(UTC),
                    now + timedelta(seconds=timeout))
        if until <= now:
            raise LiveExecutionCustodyError('native_execution_deadline_expired')
        deadline = time.monotonic() + (until - now).total_seconds()
        plan = {'execution_deadline_at': until.isoformat().replace('+00:00', 'Z'),
                'containment_argv_sha256': sha256_hex(canonical_json(sealed))}
        material = {**body, 'launch_plan': plan}
        pid = 'native-process-' + sha256_hex(canonical_json(material))
        intent = {**material, 'process_id': pid, 'effect_id': pid}
        try:
            right = _NativeRight(path, intent)
        except FileExistsError:
            return self._recover(path, body, command, timeout)
        control = _NativeControl(e, right)
        process = None
        attempted = None
        stdout, stderr, timed_out = b'', b'', False
        started = now.isoformat()
        with SandboxReadiness() as readiness:
            try:
                if not control.prepare(sealed):
                    raise LiveExecutionCustodyError('shared_admission_refused')
                if time.monotonic() >= deadline:
                    raise LiveExecutionCustodyError('native_deadline_expired_before_creation')
                before = control.sample_clock()
                attempted = before['utc']
                _write_exclusive(path, 'possible-creation.json', canonical_json(before))
                actual = [str(readiness.block_reader) if p == '{block_fd}' else
                          str(readiness.info_writer) if p == '{info_fd}' else p for p in argv]
                try:
                    process = subprocess.Popen(actual, cwd=cwd, env=env, stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        pass_fds=readiness.pass_fds, start_new_session=True)
                except BaseException as error:
                    with preserve_launch_error(error, 'native_creation_uncertainty'):
                        control.creation(before, None, pid=None)
                    raise
                readiness.child_started()
                control.creation(before, control.sample_clock(), pid=process.pid)
                control.adopt_namespace(readiness.observe(process.pid, deadline=deadline), post_monitor_timeout_ms=1000)
                control.observe_liveness()
                if time.monotonic() >= deadline:
                    raise LiveExecutionCustodyError('native_deadline_expired_before_release')
                readiness.release()
                try:
                    stdout, stderr = process.communicate(b'\x01' + (input or b''), timeout=max(0, deadline-time.monotonic()))
                except subprocess.TimeoutExpired:
                    timed_out = True
                    _terminate_process_group(process, force=True)
                    stdout, stderr = process.communicate(timeout=1)
                control.close_namespace_observation(deadline=deadline)
                c = right.complete(attempted_at=attempted, process=process, stdout=stdout,
                    stderr=stderr, timed_out=timed_out, started=started)
                control.reconcile(c)
            except BaseException as error:
                if process is not None:
                    with preserve_launch_error(error, 'native_group_abort'):
                        _terminate_process_group(process, force=True)
                with preserve_launch_error(error, 'native_readiness_abort'):
                    readiness.abort()
                if process is not None:
                    with preserve_launch_error(error, 'native_monitor_reap'):
                        process.wait(timeout=1)
                    for stream in (process.stdin, process.stdout, process.stderr):
                        with preserve_launch_error(error, 'native_stream_close'):
                            stream.close()
                with preserve_launch_error(error, 'native_namespace_close'):
                    control.close_namespace_observation(deadline=deadline)
                if right.completion is None:
                    with preserve_launch_error(error, 'native_completion_publish'):
                        right.complete(attempted_at=attempted, process=process, stdout=stdout, stderr=stderr,
                            timed_out=timed_out, started=started, error=type(error).__name__ + ':' + str(error))
                with preserve_launch_error(error, 'native_reconcile'):
                    control.reconcile(right.completion)
                raise
        return self._result(command, timeout, right.completion, stdout, stderr)

    def _retained(self, path, expected=None):
        if path.is_symlink():
            raise LiveExecutionCustodyError('native_custody_symlink')
        d = _read_canonical_document(path / 'intent.json')
        material = {k: v for k, v in d.items() if k not in {'process_id', 'effect_id'}}
        stable = {k: v for k, v in material.items() if k != 'launch_plan'}
        pid = 'native-process-' + sha256_hex(canonical_json(material))
        if (d['process_id'] != pid or d['effect_id'] != pid
            or d['enrollment_sha256'] != self.receipt_sha
            or self._key(d['subject'], d['assignment']) != path.name
            or d['launch_plan']['containment_argv_sha256'] != sha256_hex(canonical_json(d['argv']))
            or (expected is not None and stable != expected)):
            raise LiveExecutionCustodyError('native_retained_intent_changed')
        right = _NativeRight(path, d, recovered=True)
        if right.completion is not None:
            c = right.completion
            if (c['schema_version'] != 'caplab-native-process-completion/1' or c['process_id'] != pid
                or type(c['timed_out']) is not bool or type(c['outputs_complete']) is not bool
                or (c['exit_code'] is not None and type(c['exit_code']) is not int)
                or c['invocation_state'] not in {'invoked', 'not_invoked'}
                or (c['outputs_complete'] and (c['error'] is not None or c['exit_code'] is None))
                or (c['launch_attempted_at'] is None and (path / 'possible-creation.json').exists())):
                raise LiveExecutionCustodyError('native_retained_completion_changed')
            for name in ('stdout', 'stderr'):
                if sha256_hex(_read(path / name)) != c[name + '_sha256']:
                    raise LiveExecutionCustodyError('native_retained_output_changed')
        return right

    def _recover(self, path, body, command, timeout):
        try:
            right = self._retained(path, body)
        except FileNotFoundError:
            raise LiveExecutionCustodyError('native_custody_incomplete_no_retry') from None
        _NativeControl(self.enrollments[body['subject']], right).reconcile(right.completion)
        if right.completion is None or not right.completion['outputs_complete']:
            raise LiveExecutionCustodyError('native_outcome_unresolved_no_retry')
        return self._result(command, timeout, right.completion,
            _read(path / 'stdout'), _read(path / 'stderr'))

    @staticmethod
    def _result(command, timeout, completion, stdout, stderr):
        if completion['timed_out']:
            raise subprocess.TimeoutExpired(command, timeout, output=stdout, stderr=stderr)
        return subprocess.CompletedProcess(command, completion['exit_code'], stdout, stderr)

    def reconcile(self):
        results = []
        for path in sorted(self.root.iterdir()):
            if not path.is_dir():
                raise LiveExecutionCustodyError('native_unexpected_custody_entry')
            try:
                right = self._retained(path)
            except FileNotFoundError:
                results.append({'status': 'hold', 'code': 'native_custody_incomplete'})
                continue
            results.append(_NativeControl(self.enrollments[right.intent['subject']], right).reconcile(right.completion))
        return results


def load_native_admission(path, manifest, *, family):
    from caplab.preference.native_live import _CLAUDE_CONFIG, _CODEX_CONFIG
    c = NativeCalibrationAdmission.read(path, manifest, family=family)
    c.validate_native_homes({'fable': str(_CLAUDE_CONFIG), 'gpt': str(_CODEX_CONFIG), 'platform': None})
    for subject in ('fable', 'gpt'):
        native = c.enrollments[subject].selection.native
        declared = manifest['_instrument']['agent_systems'][subject]
        if any(native[k] != declared[k] for k in ('model_id', 'native_harness_id', 'effort')):
            raise LiveExecutionCustodyError('native_catalog_tuple_mismatch')
    return c


def execute_enrolled_trial(config, manifest, *, family, slot_index, attempt_kind, prior_attempts=None):
    """Project retained native outputs after a crash; never re-launch an attempt."""
    from caplab.preference import native_live as preference
    from caplab.review_dissent import native_live as review
    authorities = {'adr-0041', 'adr-0042'} if family == 'preference' else {'adr-0044'}
    if (manifest.get('status') != 'active' or manifest.get('authority') not in authorities
        or manifest.get('_verified_manifest_sha256') != manifest.get('manifest_sha256')
        or datetime.fromisoformat(manifest['expires_at']) < datetime.now(UTC)):
        raise LiveExecutionCustodyError('native_trial_not_authorized')
    module = preference if family == 'preference' else review
    loader = preference.load_native_custody_attempts if family == 'preference' else review.load_native_review_attempts
    assessor = preference.assess_native_attempts if family == 'preference' else review.assess_native_review_attempts
    prepare = preference.prepare_native_trial if family == 'preference' else review.prepare_native_review_trial
    observe = preference.record_native_observation if family == 'preference' else review.record_native_review_observation
    control = load_native_admission(config, manifest, family=family)
    parent = Path(manifest['storage']['raw_custody_root']) / 'attempts'
    if type(slot_index) is not int or attempt_kind not in {'primary', 'replacement'}:
        raise LiveExecutionCustodyError('native_trial_assignment_invalid')
    matches = sorted(parent.glob(f'a*-s{slot_index+1:02d}-{attempt_kind}'))
    if len(matches) > 1:
        raise LiveExecutionCustodyError('native_trial_assignment_ambiguous')
    recovered = bool(matches)
    if recovered:
        attempt_root = matches[0]
        launch = module._read_json(attempt_root / 'launch.json')
        body = dict(launch)
        claimed = body.pop('launch_sha256', None)
        if (module._digest(body) != claimed or launch['manifest_sha256'] != manifest['manifest_sha256']
            or launch['campaign_id'] != manifest['campaign_id'] or launch['slot_index'] != slot_index
            or launch['attempt_kind'] != attempt_kind
            or launch['schema'] != f'caplab.{family}.native-launch/v1'
            or type(launch['attempt_number']) is not int or launch['attempt_number'] <= 0
            or attempt_root.name != f'a{launch["attempt_number"]:02d}-s{slot_index+1:02d}-{attempt_kind}'):
            raise LiveExecutionCustodyError('native_trial_launch_changed')
        item, expected_subject = manifest['_instrument']['execution_order'][slot_index].split(':', 1)
        if (launch['subject_id'] != expected_subject
            or launch['tuple_id'] != manifest['_instrument']['agent_systems'][expected_subject]['tuple_id']
            or (family == 'preference' and launch['task_id'] != item)
            or (family == 'review-dissent' and (launch['cell_id'] != item or
                launch['public_task_id'] != manifest['_instrument']['cells'][item]['public_task_id']))):
            raise LiveExecutionCustodyError('native_trial_launch_assignment_changed')
        command = launch['command']
    else:
        recorded = loader(manifest)
        if prior_attempts is not None and list(prior_attempts) != recorded:
            raise LiveExecutionCustodyError('native_prior_attempts_changed')
        state = assessor(manifest, recorded)
        pending = state['pending_replacement_for']
        if (state['complete'] or state['stop_reason'] is not None
            or (pending is None and (attempt_kind != 'primary' or slot_index != state['next_slot_index']))
            or (pending is not None and (attempt_kind != 'replacement' or slot_index != pending))):
            raise LiveExecutionCustodyError('native_next_action_mismatch')
        versions = preference.preflight_native_runtime(manifest, shared_admission=control,
            assignment=f'trial:s{slot_index+1:02d}:{attempt_kind}:preflight')
        attempt_root, command = prepare(manifest, slot_index=slot_index, attempt_kind=attempt_kind,
            prior_attempts=recorded, observed_versions=versions)
        launch = module._read_json(attempt_root / 'launch.json')
    subject = launch['subject_id']
    assignment = 'trial:' + attempt_root.name
    if recovered and not (control.root / control._key(subject, assignment)).exists():
        raise LiveExecutionCustodyError('native_prepared_attempt_unresolved_no_retry')
    if recovered:
        retained_right = control._retained(control.root / control._key(subject, assignment))
        c = retained_right.completion
        if c is not None and c['outputs_complete']:
            expected = _native_completion(module, manifest, launch, c)
            for name, data in [('native.stdout', _read(retained_right.custody_root / 'stdout')),
                ('native.stderr', _read(retained_right.custody_root / 'stderr')),
                ('completion.json', module._canonical(expected) + b'\n')]:
                p = attempt_root / name
                if p.exists() and _read(p) != data:
                    raise LiveExecutionCustodyError('native_trial_publication_changed')
            if (attempt_root / 'observation.json').exists():
                loader(manifest)
    task = launch['task_id'] if family == 'preference' else launch['public_task_id']
    timeout = manifest['limits']['trial_wall_clock_minutes'] * 60
    try:
        done = control.run(command, cwd=attempt_root / 'input' / task, subject=subject,
            assignment=assignment, timeout=timeout, env=preference._launcher_environment(),
            native_launch_sha256=launch['launch_sha256'])
        stdout, stderr = done.stdout, done.stderr
    except subprocess.TimeoutExpired as error:
        stdout, stderr = error.stdout or b'', error.stderr or b''
    retained = control.completion_for(subject, assignment)
    if retained is None:
        raise LiveExecutionCustodyError('native_trial_outcome_unresolved')
    completion = _native_completion(module, manifest, launch, retained)
    for name, data in [('native.stdout', stdout), ('native.stderr', stderr),
                       ('completion.json', module._canonical(completion) + b'\n')]:
        path = attempt_root / name
        if path.exists():
            if _read(path) != data:
                raise LiveExecutionCustodyError('native_trial_publication_changed')
        else:
            module._exclusive_bytes(path, data)
    if not (attempt_root / 'observation.json').exists():
        observe(manifest, attempt_root=attempt_root)
    loader(manifest)  # verifies native observation/output lineage, including a recovered projection
    return attempt_root


def _native_completion(module, manifest, launch, retained):
    family = 'preference' if launch['schema'] == 'caplab.preference.native-launch/v1' else 'review-dissent'
    c = {'schema': f'caplab.{family}.native-completion/v1',
        'campaign_id': manifest['campaign_id'], 'manifest_sha256': manifest['manifest_sha256'],
        'launch_sha256': launch['launch_sha256'], 'started_at': retained['started_at'],
        'finished_at': retained['finished_at'],
        'duration_seconds': format((datetime.fromisoformat(retained['finished_at']) -
                                    datetime.fromisoformat(retained['started_at'])).total_seconds(), '.6f'),
        'return_code': None if retained['timed_out'] else retained['exit_code'],
        'timed_out': retained['timed_out'],
        'stdout_sha256': retained['stdout_sha256'], 'stderr_sha256': retained['stderr_sha256']}
    c['completion_sha256'] = module._digest(c)
    return c


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(prog='python -m caplab.runtime.native_admission')
    commands = parser.add_subparsers(dest='command', required=True)
    domain = commands.add_parser('domain')
    domain.add_argument('--custody', type=Path, required=True)
    args = parser.parse_args(argv)
    print(json.dumps({'custody_domain_id': initialize_domain(args.custody)}, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
