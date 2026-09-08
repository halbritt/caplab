"""Compare retained Claude root session fields without reconstructing a conversation."""

from __future__ import annotations

from contextlib import ExitStack
from pathlib import Path, PurePosixPath

from caplab.codex_capture_link import _retained_bytes
from caplab.native_collection_verify import verify_native_collection
from caplab.review_dissent.native import NativeReviewContractError, _native_events, _native_session_evidence
from caplab.task_capture_verify import CaptureVerificationError, _Reader, _open, _require, verify_task_capture


def _events(content: bytes) -> list[dict]:
    _require(content.endswith(b'\n'), 'identity JSONL lacks final newline')
    try:
        events = _native_events(content)
    except (NativeReviewContractError, RecursionError) as error:
        raise CaptureVerificationError('invalid identity JSONL') from error
    _require(bool(events) and all(isinstance(e.get('type'), str) and e['type'].strip() for e in events),
             'identity records require nonempty type')
    return events


def claude_root_session_fields(stdout: bytes, transcript: bytes, *, session_id: str) -> dict:
    """Check explicit fields in bounded caller-owned bytes; never follow parentUuid.

    Missing IDs on root user/assistant records fail. Non-root scopes cannot
    satisfy root evidence. No model, effort, version or conversation claim.
    """
    _require(isinstance(session_id, str) and bool(session_id.strip()), 'invalid expected session ID')
    events = _events(stdout)
    observations, errors = _native_session_evidence(events)
    _require(not errors, 'invalid or conflicting stdout session evidence')
    initial = [e for e in events if e['type'] == 'system' and e.get('subtype') == 'init']
    _require(len(initial) == 1 and initial[0] is events[0] and initial[0].get('session_id') == session_id,
             'stdout requires one initial configured root session')
    roots = [o for o in observations if o['parent_tool_use_id'] is None]
    _require(all(o['session_id'] == session_id for o in roots), 'stdout root session differs from configured ID')
    for event in events:
        if event['type'] in ('user', 'assistant', 'result') and event.get('parent_tool_use_id') is None:
            _require(event.get('session_id') == session_id, 'stdout root message lacks configured session ID')

    records = _events(transcript)
    root_messages = nonroot_messages = 0
    for entry in records:
        for flag in ('isSidechain', 'isMeta'):
            _require(flag not in entry or type(entry[flag]) is bool, 'invalid persisted scope flag')
        team = entry.get('teamName')
        _require(team is None or isinstance(team, str) and bool(team.strip()), 'invalid persisted team scope')
        nonroot = entry.get('isSidechain', False) or entry.get('isMeta', False) or team is not None
        if 'sessionId' in entry:
            observed = entry['sessionId']
            _require(isinstance(observed, str) and bool(observed.strip()), 'invalid persisted session ID')
            _require(nonroot or observed == session_id, 'persisted root session differs from configured ID')
        if entry['type'] not in ('user', 'assistant'):
            continue
        _require(isinstance(entry.get('uuid'), str) and bool(entry['uuid'].strip()),
                 'persisted message lacks UUID')
        if nonroot:
            nonroot_messages += 1
        else:
            _require(entry.get('sessionId') == session_id, 'persisted root message lacks configured session ID')
            root_messages += 1
    _require(root_messages > 0, 'persisted transcript has no root messages')
    return {'session_id': session_id, 'stdout_root_observations': len(roots),
            'stdout_nonroot_observations': len(observations) - len(roots),
            'persisted_root_messages': root_messages, 'persisted_nonroot_messages': nonroot_messages,
            'persisted_records': len(records)}


def link_claude_root(
    policy_path: Path, task_custody: Path, collection_custody: Path, *,
    expected_attempt_sha256: str, expected_collection_sha256: str,
    max_receipt_bytes: int, max_identity_bytes: int,
) -> dict:
    """Verify both bundles, then compare configured and retained root session IDs.

    Each bundle and the joint metadata reread has its own receipt allowance.
    Stdout plus transcript share the identity allowance. Custody must be quiescent.
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
        _require(subject['native_harness_id'] == 'claude-code', 'root linkage requires a Claude collection')
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
        session_id = invocation['session_id']
        session_entries = [e for e in collection['entries'] if e['path'].startswith('session_search_root/')]
        matches = [e for e in session_entries if PurePosixPath(e['path']).name == session_id + '.jsonl']
        _require(len(matches) == 1, 'root transcript must have exactly one exact retained filename candidate')
        selected = matches[0]
        _require(selected['kind'] == 'file', 'root transcript candidate must be a retained regular file')
        _require(len(PurePosixPath(selected['path']).parts) == 3, 'root transcript must be directly in a project directory')
        objects = stack.enter_context(_open(native_root, 'objects', directory=True))
        transcript = _retained_bytes(objects, selected['object'], selected, max_identity_bytes - len(stdout))
        fields = claude_root_session_fields(stdout, transcript, session_id=session_id)
    return {'schema': 'caplab.claude-root-capture-link/v1',
            'attempt_sha256': expected_attempt_sha256, 'collection_sha256': expected_collection_sha256,
            'invocation_sha256': invocation['invocation_sha256'], 'profile_sha256': invocation['profile_sha256'],
            'configured_tuple_id': subject['tuple_id'], 'stdout_sha256': stdout_entry['sha256'],
            'transcript_path': selected['path'], 'transcript_sha256': selected['sha256'],
            'session_fields': fields, 'root_id_agrees': True, 'recorded_task_root_agrees': True,
            'reported_tuple_agrees': None, 'executed_invocation_bound': False,
            'process_capture_complete': task_check['capture_complete'],
            'process_return_code': task_check['return_code'], 'process_termination': task_check['termination'],
            'identity_bytes': len(stdout) + len(transcript),
            'bundle_receipt_bytes': collection_check['verified_receipt_bytes'] + task_check['verified_receipt_bytes'],
            'link_receipt_bytes': max_receipt_bytes - reader.remaining,
            'other_session_files': sum(e['kind'] == 'file' and e is not selected for e in session_entries),
            'conversation_chain_verified': False, 'child_linkage_verified': False, 'native_capture_complete': None,
            'interpretation': 'retained root session fields agree; no tuple attestation, executed-invocation binding or eligibility'}
