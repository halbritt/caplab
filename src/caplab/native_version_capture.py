"""Version-only native execution in a fresh no-network prepared namespace."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
import os
from pathlib import Path

from caplab.native_collection import _receipt, _retain_receipt
from caplab.native_runtime import _validated_invocation
from caplab.preference.native_live import _launcher_environment
from caplab.process_capture import capture_process, seal_capture_json
from caplab.task_capture_verify import _digest, _open, _read_file, _require


@dataclass(frozen=True)
class NativeVersionCaptureLimits:
    max_receipt_bytes: int
    max_entrypoint_bytes: int
    max_stream_bytes: int
    timeout_seconds: float

    def __post_init__(self):
        _require(all(type(v) is int and v > 0 for v in
                     (self.max_receipt_bytes, self.max_entrypoint_bytes, self.max_stream_bytes)),
                 'version byte limits must be positive integers')
        _require(type(self.timeout_seconds) in (int, float) and math.isfinite(self.timeout_seconds)
                 and self.timeout_seconds > 0, 'version timeout must be positive and finite')


def _resolved(path: Path, *, directory: bool) -> Path:
    path = Path(path)
    _require(path.is_absolute() and path != Path('/') and path.resolve() == path,
             'version source must have a resolved absolute path')
    _require(path.is_dir() if directory else path.is_file(), 'version source has wrong kind')
    return path


def _disjoint(left: Path, right: Path) -> bool:
    return not left.is_relative_to(right) and not right.is_relative_to(left)


def _version_command(plan: dict, task: Path, runtime: Path, harness: Path) -> list[str]:
    executable = plan['version_command'][0]
    entrypoint = '/opt/native/bin/codex.js' if executable == 'codex' else '/opt/native'
    command = ['/usr/bin/bwrap', '--unshare-all', '--die-with-parent', '--new-session', '--clearenv',
               '--ro-bind', '/usr', '/usr', '--symlink', 'usr/bin', '/bin',
               '--symlink', 'usr/lib', '/lib', '--symlink', 'usr/lib64', '/lib64',
               '--proc', '/proc', '--dev', '/dev', '--tmpfs', '/tmp', '--dir', '/opt', '--dir', '/toolbin',
               '--ro-bind', str(harness), '/opt/native', '--symlink', entrypoint, '/toolbin/' + executable,
               '--ro-bind', str(task), '/work', '--bind', str(runtime), '/episode', '--chdir', '/work']
    for key, value in sorted(plan['environment'].items()):
        command += ['--setenv', key, value]
    return command + ['--', *plan['version_command']]


def capture_native_version(
    policy_path: Path, preparation_root: Path, harness_source: Path, *,
    expected_preparation_sha256: str, expected_entrypoint_sha256: str,
    output_dir: Path, limits: NativeVersionCaptureLimits,
) -> dict:
    """Capture only the canonical --version command; caller owns probe authority.

    Sources and parents must stay trusted/quiescent. Entrypoint pinning does not
    pin the package's dependencies, system runtime or provider. Partial output
    survives errors; a version probe is not a study attempt or replay reservation.
    """
    _require(isinstance(limits, NativeVersionCaptureLimits), 'invalid version limits')
    _digest(expected_entrypoint_sha256)
    root = _resolved(preparation_root, directory=True)
    with _open(None, root, directory=True) as fd:
        preparation, prep_raw = _receipt(fd, 'preparation.json', expected_preparation_sha256,
            'caplab.native-runtime-preparation/v1', limits.max_receipt_bytes)
        invocation, invocation_raw = _receipt(fd, 'invocation.json', preparation.get('invocation_file_sha256'),
            'caplab.native-capture-invocation/v1', limits.max_receipt_bytes - len(prep_raw))
    plan = _validated_invocation(policy_path, invocation, preparation.get('invocation_sha256'))
    _require(plan['cwd'] == '/work' and plan['runtime_root'] == '/episode', 'unsupported version namespace paths')
    runtime = _resolved(root / 'runtime', directory=True)
    try:
        task = _resolved(Path(preparation['mounts']['task']['source']), directory=True)
    except (KeyError, TypeError) as error:
        raise ValueError('version preparation lacks task source') from error
    expected_mounts = {'task': {'source': str(task), 'destination': '/work', 'access': 'rw'},
                       'runtime': {'source': str(runtime), 'destination': '/episode', 'access': 'rw'}}
    _require(preparation.get('mounts') == expected_mounts and preparation.get('custody_root') == str(root)
             and preparation.get('runtime_root') == str(runtime) and _disjoint(task, root),
             'version preparation layout differs')
    codex = plan['base_subject']['native_harness_id'] == 'codex'
    harness = _resolved(harness_source, directory=codex)
    _require(_disjoint(harness, task) and _disjoint(harness, root), 'harness overlaps prepared writable state')
    entrypoint = _resolved(harness / 'bin/codex.js' if codex else harness, directory=False)
    _require(os.access(entrypoint, os.X_OK), 'native entrypoint is not executable')
    _, entry_bytes, entry_hash = _read_file(None, entrypoint, limits.max_entrypoint_bytes, retain=False)
    _require(entry_hash == expected_entrypoint_sha256, 'native entrypoint digest differs')
    output_dir = Path(output_dir)
    _require(output_dir.is_absolute() and output_dir.parent.resolve() == output_dir.parent
             and all(_disjoint(output_dir, p) for p in (root, task, harness)), 'unsafe version output root')
    command = _version_command(plan, task, runtime, harness)
    environment = _launcher_environment()
    output_dir.mkdir(mode=0o700)
    output_dir.chmod(0o700)
    _retain_receipt(output_dir / 'preparation.json', prep_raw)
    _retain_receipt(output_dir / 'invocation.json', invocation_raw)
    intent = {'schema': 'caplab.native-version-intent/v1', 'preparation_sha256': expected_preparation_sha256,
              'invocation_sha256': plan['invocation_sha256'], 'command': command, 'environment': environment,
              'cwd': str(task), 'harness_source': str(harness), 'entrypoint_sha256': entry_hash,
              'entrypoint_bytes': entry_bytes, 'limits': asdict(limits), 'network': 'unshared',
              'task_access': 'read-only', 'purpose': 'version-only; no model prompt'}
    intent_hash = seal_capture_json(output_dir, 'intent.json', intent)
    process = capture_process(command, cwd=task, environment=environment, output_dir=output_dir / 'process',
                              max_stream_bytes=limits.max_stream_bytes, timeout_seconds=limits.timeout_seconds)
    _, _, process_hash = _read_file(None, output_dir / 'process/capture.json', limits.max_receipt_bytes, retain=False)
    _, final_bytes, final_hash = _read_file(None, entrypoint, limits.max_entrypoint_bytes, retain=False)
    _require((final_bytes, final_hash) == (entry_bytes, entry_hash), 'native entrypoint changed during probe')
    report = {'schema': 'caplab.native-version-capture/v1', 'intent_sha256': intent_hash,
              'preparation_sha256': expected_preparation_sha256, 'invocation_sha256': plan['invocation_sha256'],
              'configured_tuple_id': plan['base_subject']['tuple_id'], 'entrypoint_sha256': entry_hash,
              'process_capture_sha256': process_hash, 'process': process,
              'native_identity_verified': False, 'binding_complete': False,
              'interpretation': 'bounded version-command output; no model execution or complete Binding attestation'}
    seal_capture_json(output_dir, 'version.json', report)
    return report
