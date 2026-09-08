"""Verify retained version-probe custody without reading an installation."""

from __future__ import annotations

import json
from pathlib import Path

from caplab.native_collection_verify import _host_path
from caplab.native_runtime import _validated_invocation
from caplab.native_version_capture import NativeVersionCaptureLimits, _disjoint, _version_command
from caplab.preference.native_live import _launcher_environment
from caplab.task_capture_verify import CaptureVerificationError, _Reader, _count, _digest, _open, _process, _require


def verify_native_version(
    policy_path: Path, custody: Path, *, expected_version_sha256: str,
    max_receipt_bytes: int, max_stream_bytes: int,
) -> dict:
    """Check five anchored receipts, recorded command and raw stream integrity.

    Caller supplies an independent final digest and quiescent custody with stable
    trusted parents. Recorded source paths are inert. Limits bound combined JSON
    and stream bytes separately; no execution, version-text interpretation or
    native identity authentication occurs. Errors leave custody unchanged.
    """
    _digest(expected_version_sha256)
    _require(all(type(value) is int and value > 0 for value in (max_receipt_bytes, max_stream_bytes)),
             'verification byte limits must be positive integers')
    custody = Path(custody)
    _require(custody.is_absolute() and custody.parent.resolve() == custody.parent,
             'custody must have an absolute resolved parent')
    reader = _Reader(max_receipt_bytes)
    with _open(None, custody, directory=True) as root:
        version = reader.receipt(root, 'version.json', expected_version_sha256,
                                 'caplab.native-version-capture/v1')
        intent = reader.receipt(root, 'intent.json', version.get('intent_sha256'),
                                'caplab.native-version-intent/v1')
        try:
            limits = NativeVersionCaptureLimits(**intent['limits'])
        except (KeyError, TypeError, ValueError, OverflowError) as error:
            raise CaptureVerificationError('invalid version capture limits') from error
        remaining = reader.remaining
        preparation = reader.receipt(root, 'preparation.json', intent.get('preparation_sha256'),
                                     'caplab.native-runtime-preparation/v1')
        invocation = reader.receipt(root, 'invocation.json', preparation.get('invocation_file_sha256'),
                                    'caplab.native-capture-invocation/v1')
        _require(remaining - reader.remaining <= limits.max_receipt_bytes,
                 'source receipts exceed version intent allowance')
        try:
            plan = _validated_invocation(policy_path, invocation, preparation.get('invocation_sha256'))
        except ValueError as error:
            raise CaptureVerificationError('invalid version invocation') from error
        _require(plan['cwd'] == '/work' and plan['runtime_root'] == '/episode',
                 'unsupported version namespace paths')
        prepared_root = _host_path(preparation.get('custody_root'), 'prepared root')
        runtime = prepared_root / 'runtime'
        task = _host_path(intent.get('cwd'), 'version task root')
        harness = _host_path(intent.get('harness_source'), 'version harness source')
        _require(_disjoint(task, prepared_root) and _disjoint(harness, task)
                 and _disjoint(harness, prepared_root), 'version source roots overlap')
        _require(preparation.get('runtime_root') == str(runtime) and preparation.get('mounts') == {
            'task': {'source': str(task), 'destination': '/work', 'access': 'rw'},
            'runtime': {'source': str(runtime), 'destination': '/episode', 'access': 'rw'},
        }, 'version preparation layout differs')
        _require(intent.get('command') == _version_command(plan, task, runtime, harness)
                 and intent.get('environment') == _launcher_environment(),
                 'recorded version command or environment differs')
        _require(intent.get('network') == 'unshared' and intent.get('task_access') == 'read-only'
                 and intent.get('purpose') == 'version-only; no model prompt', 'version purpose or access differs')
        entrypoint_sha = _digest(intent.get('entrypoint_sha256'))
        entrypoint_bytes = _count(intent.get('entrypoint_bytes'), 'entrypoint bytes')
        _require(entrypoint_bytes <= limits.max_entrypoint_bytes, 'entrypoint exceeds recorded allowance')
        _require(version.get('preparation_sha256') == intent['preparation_sha256']
                 and version.get('invocation_sha256') == intent.get('invocation_sha256') == plan['invocation_sha256']
                 and version.get('configured_tuple_id') == plan['base_subject']['tuple_id']
                 and version.get('entrypoint_sha256') == entrypoint_sha, 'version identity links differ')
        _require(version.get('native_identity_verified') is False and version.get('binding_complete') is False,
                 'version capture asserts unsupported identity verification')
        with _open(root, 'process', directory=True) as process_root:
            remaining = reader.remaining
            process = reader.receipt(process_root, 'capture.json', version.get('process_capture_sha256'),
                                     'caplab.process-capture/v1')
            _require(remaining - reader.remaining <= limits.max_receipt_bytes,
                     'process receipt exceeds version intent allowance')
            _require(json.dumps(version.get('process'), sort_keys=True) == json.dumps(process, sort_keys=True),
                     'embedded process differs from linked receipt')
            streams = process.get('streams')
            _require(isinstance(streams, dict) and set(streams) == {'stdout', 'stderr'}
                     and all(isinstance(entry, dict) for entry in streams.values()), 'invalid version streams')
            total = sum(_count(entry.get('bytes'), 'stream bytes') for entry in streams.values())
            _require(total <= max_stream_bytes, 'version streams exceed verification allowance')
            # The shared process checker consumes max_stream_bytes and timeout_seconds.
            _process(process_root, process, limits)
    return {'schema': 'caplab.native-version-inspection/v1', 'version_sha256': expected_version_sha256,
            'integrity_verified': True, 'recorded_version_command_agrees': True,
            'preparation_sha256': intent['preparation_sha256'], 'invocation_sha256': plan['invocation_sha256'],
            'configured_tuple_id': plan['base_subject']['tuple_id'], 'profile_sha256': plan['profile_sha256'],
            'entrypoint_sha256': entrypoint_sha, 'entrypoint_bytes': entrypoint_bytes,
            'process_capture_sha256': version['process_capture_sha256'],
            'process_capture_complete': process['streams_complete'], 'termination': process['termination'],
            'return_code': process['return_code'], 'retained_stream_bytes': total,
            'streams': {name: {key: entry[key] for key in ('path', 'bytes', 'sha256', 'eof')}
                        for name, entry in streams.items()},
            'verified_receipt_bytes': max_receipt_bytes - reader.remaining,
            'native_identity_verified': False, 'binding_complete': False,
            'interpretation': 'retained version-probe integrity and recorded command agreement; no version-text or full Binding verification'}
