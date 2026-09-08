"""Link retained Codex root observations without granting execution or eligibility."""

from __future__ import annotations

from contextlib import ExitStack
from pathlib import Path, PurePosixPath

from caplab.artifact_rater import CalibrationError, _ROLLOUT_NAME, attest_rollout_capture
from caplab.codex_events import CodexEventError, codex_thread_id
from caplab.native_collection_verify import verify_native_collection
from caplab.task_capture_verify import CaptureVerificationError, _Reader, _open, _read_file, _require, verify_task_capture


def _retained_bytes(parent: int, name: str, entry: dict, allowance: int) -> bytes:
    _require(entry['bytes'] <= allowance, 'identity bytes exceed allowance')
    raw, size, digest = _read_file(parent, name, entry['bytes'], retain=True)
    _require(size == entry['bytes'] and digest == entry['sha256'], 'identity payload differs from anchored entry')
    return raw


def link_codex_root(
    policy_path: Path, task_custody: Path, collection_custody: Path, *,
    expected_attempt_sha256: str, expected_collection_sha256: str,
    max_receipt_bytes: int, max_identity_bytes: int,
) -> dict:
    """Verify both bundles and compare root session/model/effort observations.

    Each bundle verification and the combined metadata reread has its own
    max_receipt_bytes allowance. Retained stdout plus selected rollout share
    max_identity_bytes. Caller owns independent anchors and quiescent custody.
    """
    _require(type(max_identity_bytes) is int and max_identity_bytes > 0, 'invalid identity byte allowance')
    collection_check = verify_native_collection(policy_path, collection_custody,
        expected_collection_sha256=expected_collection_sha256, max_receipt_bytes=max_receipt_bytes)
    task_check = verify_task_capture(task_custody, expected_attempt_sha256=expected_attempt_sha256,
                                     max_receipt_bytes=max_receipt_bytes)
    reader = _Reader(max_receipt_bytes)
    with ExitStack() as stack:
        native_root = stack.enter_context(_open(None, collection_custody, directory=True))
        task_root = stack.enter_context(_open(None, task_custody, directory=True))
        collection = reader.receipt(native_root, 'collection.json', expected_collection_sha256,
                                    'caplab.native-output-collection/v1')
        intent = reader.receipt(native_root, 'intent.json', collection['intent_sha256'],
                                'caplab.native-collection-intent/v1')
        preparation = reader.receipt(native_root, 'preparation.json', intent['preparation_sha256'],
                                     'caplab.native-runtime-preparation/v1')
        invocation = reader.receipt(native_root, 'invocation.json', preparation['invocation_file_sha256'],
                                    'caplab.native-capture-invocation/v1')
        subject = invocation['base_subject']
        _require(subject['native_harness_id'] == 'codex', 'root linkage requires a Codex collection')
        attempt = reader.receipt(task_root, 'attempt.json', expected_attempt_sha256,
                                 'caplab.task-attempt-capture/v1')
        task_intent = reader.receipt(task_root, 'intent.json', attempt['intent_sha256'],
                                     'caplab.task-capture-intent/v1')
        try:
            recorded_task = preparation['mounts']['task']['source']
        except (KeyError, TypeError) as error:
            raise CaptureVerificationError('preparation lacks task source') from error
        _require(task_intent['cwd'] == recorded_task, 'captured task differs from prepared task')
        process_root = stack.enter_context(_open(task_root, 'process', directory=True))
        process = reader.receipt(process_root, 'capture.json', attempt['process_capture_sha256'],
                                 'caplab.process-capture/v1')
        stdout_entry = process['streams']['stdout']
        stdout = _retained_bytes(process_root, 'native.stdout', stdout_entry, max_identity_bytes)
        try:
            thread_id = codex_thread_id(stdout)
        except (CodexEventError, RecursionError) as error:
            raise CaptureVerificationError('captured stdout has no unambiguous Codex root ID') from error
        session_entries = [entry for entry in collection['entries']
                           if entry['path'].startswith('session_search_root/')]
        matches = []
        for entry in session_entries:
            match = _ROLLOUT_NAME.fullmatch(PurePosixPath(entry['path']).name)
            if match and match[1] == thread_id:
                matches.append(entry)
        _require(len(matches) == 1, 'root rollout must have exactly one exact retained filename candidate')
        selected = matches[0]
        _require(selected['kind'] == 'file', 'root rollout candidate must be a retained regular file')
        objects = stack.enter_context(_open(native_root, 'objects', directory=True))
        rollout = _retained_bytes(objects, selected['object'], selected, max_identity_bytes - len(stdout))
        try:
            attestation = attest_rollout_capture(rollout, thread_id, rollout_locator=selected['path'])
        except (CalibrationError, UnicodeError, RecursionError) as error:
            raise CaptureVerificationError('retained root rollout lacks consistent tuple attestation') from error
        _require(attestation['model'] == subject['model_id'] and attestation['effort'] == subject['effort'],
                 'reported root tuple differs from configured invocation')
    return {'schema': 'caplab.codex-root-capture-link/v1',
            'attempt_sha256': expected_attempt_sha256, 'collection_sha256': expected_collection_sha256,
            'invocation_sha256': invocation['invocation_sha256'], 'profile_sha256': invocation['profile_sha256'],
            'configured_tuple_id': subject['tuple_id'], 'stdout_sha256': stdout_entry['sha256'],
            'rollout': attestation, 'root_id_agrees': True, 'reported_tuple_agrees': True,
            'recorded_task_root_agrees': True, 'executed_invocation_bound': False,
            'process_capture_complete': task_check['capture_complete'],
            'process_return_code': task_check['return_code'], 'process_termination': task_check['termination'],
            'identity_bytes': len(stdout) + len(rollout),
            'bundle_receipt_bytes': collection_check['verified_receipt_bytes'] + task_check['verified_receipt_bytes'],
            'link_receipt_bytes': max_receipt_bytes - reader.remaining,
            'other_session_files': sum(entry['kind'] == 'file' and entry is not selected for entry in session_entries),
            'child_linkage_verified': False, 'native_capture_complete': None,
            'interpretation': 'retained root ID and reported tuple agreement; no executed-invocation binding or eligibility'}
