"""Link host PIDs through bounded, namespace-decoded process creation evidence."""

from dataclasses import dataclass
from pathlib import Path
import re

from caplab.task_capture_verify import _digest, _read_file, _require


_PREFIX = re.compile(r'([1-9][0-9]*)\s+(.+)')
_START = re.compile(r'(clone3?|vfork|fork)\(')
_RESUME = re.compile(r'<\.\.\. (clone3?|vfork|fork) resumed>(.*)')
_CALL = re.compile(r'(clone3?|vfork|fork)\((.*)\)\s+=\s+(.*)')
_RESULT = re.compile(r'([1-9][0-9]*)(?: /\* ([1-9][0-9]*) in strace\x27s PID NS \*/)?')
_ERROR = re.compile(r'-1 [A-Z][A-Z0-9_]* \([^\r\n]*\)')
_PARENT_FLAGS = frozenset(('CLONE_VM CLONE_FS CLONE_FILES CLONE_SIGHAND CLONE_VFORK '
    'CLONE_PARENT_SETTID CLONE_CHILD_CLEARTID CLONE_CHILD_SETTID CLONE_SYSVSEM '
    'CLONE_SETTLS CLONE_PIDFD CLONE_IO CLONE_NEWNS CLONE_NEWCGROUP CLONE_NEWUTS '
    'CLONE_NEWIPC CLONE_NEWUSER CLONE_NEWPID CLONE_NEWNET SIGCHLD 0').split())


@dataclass(frozen=True)
class ProcessCreationEvidence:
    expected_trace_sha256: str
    parent_pid: int
    child_pid: int
    max_trace_bytes: int


def _creation_records(lines, *, selected_pid=None):
    """Decode creation calls only; return their original line numbers for exec readers."""
    pending, records, consumed = {}, [], set()
    for number, line in enumerate(lines, 1):
        match = _PREFIX.fullmatch(line)
        if selected_pid is not None and (match is None or int(match[1]) != selected_pid):
            continue
        _require(match is not None, 'unsupported process trace prefix')
        pid, body = int(match[1]), match[2]
        resume, start = _RESUME.fullmatch(body), number
        if resume:
            _require(pid in pending, 'process creation resumes without entry')
            start, syscall, partial = pending.pop(pid)
            _require(resume[1] == syscall, 'process creation resumption differs')
            body = partial + resume[2]
        elif _START.match(body):
            _require(pid not in pending, 'overlapping process creation calls')
            consumed.add(number)
            if body.endswith(' <unfinished ...>'):
                pending[pid] = (number, _START.match(body)[1], body[:-len(' <unfinished ...>')])
                continue
        else:
            _require(pid not in pending or body.startswith('--- '), 'process creation interrupted by another record')
            continue
        consumed.add(number)
        call = _CALL.fullmatch(body)
        _require(call is not None, 'unsupported process creation record')
        syscall, arguments, result = call.groups()
        flags = _creation_flags(syscall, arguments.strip())
        parsed = _RESULT.fullmatch(result)
        _require(parsed is not None or _ERROR.fullmatch(result), 'invalid process creation result')
        if parsed:
            records.append({'parent_pid': pid, 'child_pid': int(parsed[2] or parsed[1]),
                'namespace_child_pid': int(parsed[1]), 'translated': parsed[2] is not None,
                'flags': flags, 'syscall': syscall,
                'entry_line': start, 'completion_line': number})
    _require(not pending, 'unfinished process creation call')
    return records, consumed


def _creation_flags(syscall, arguments):
    if syscall in ('fork', 'vfork'):
        _require(not arguments, 'unexpected fork arguments')
        return set()
    flags = re.findall(r'(?:^|[, {])flags=([A-Z0-9_|]+)(?=[,}]|$)', arguments)
    _require(len(flags) == 1 and '...' not in arguments, 'missing or abbreviated clone flags')
    observed = set(flags[0].split('|'))
    _require(observed <= _PARENT_FLAGS | {'CLONE_PARENT', 'CLONE_THREAD'}, 'unsupported clone flags')
    return observed


def _lifetimes(lines, selected):
    ended = set()
    for number, line in enumerate(lines, 1):
        match = _PREFIX.fullmatch(line)
        pid, body = int(match[1]), match[2]
        if pid not in (selected['parent_pid'], selected['child_pid']):
            continue
        _require(pid not in ended, 'process PID appears after its terminal event')
        if pid == selected['child_pid']:
            _require(number > selected['entry_line'], 'child PID appears before its creation')
        if body.startswith('+++ '):
            ended.add(pid)


def inspect_process_creation(trace_path: Path, *, evidence: ProcessCreationEvidence) -> dict:
    """Check direct parentage; caller owns trace origin, process identity and lifetime."""
    _require(isinstance(evidence, ProcessCreationEvidence), 'invalid process creation evidence')
    _digest(evidence.expected_trace_sha256)
    _require(all(type(value) is int and value > 0 for value in
                 (evidence.parent_pid, evidence.child_pid, evidence.max_trace_bytes)), 'invalid process identity or allowance')
    _require(evidence.parent_pid != evidence.child_pid, 'process parent and child overlap')
    path = Path(trace_path)
    _require(path.is_absolute() and path.parent.resolve() == path.parent, 'trace parent must be resolved')
    raw, size, digest = _read_file(None, path, evidence.max_trace_bytes, retain=True)
    _require(digest == evidence.expected_trace_sha256, 'process trace hash differs')
    _require(raw.endswith(b'\n'), 'process trace has incomplete final line')
    lines = raw.decode('ascii').splitlines()
    records, _ = _creation_records(lines)
    matches = [record for record in records if record['child_pid'] == evidence.child_pid]
    _require(len(matches) == 1, 'expected exactly one child creation')
    selected = matches[0]
    _require(selected['parent_pid'] == evidence.parent_pid, 'process creator differs')
    _require(selected['translated'], 'child PID lacks explicit namespace translation')
    _require(selected['flags'] <= _PARENT_FLAGS, 'unsupported clone parentage flags')
    _lifetimes(lines, selected)
    return {'schema': 'caplab.process-creation-inspection/v1', 'trace_sha256': digest, 'trace_bytes': size,
            'parent_pid': evidence.parent_pid, 'child_pid': evidence.child_pid,
            'namespace_child_pid': selected['namespace_child_pid'],
            'creation': {key: selected[key] for key in ('syscall', 'entry_line', 'completion_line')},
            'recorded_parentage_agrees': True, 'trace_provenance_verified': False,
            'binding_complete': False, 'native_capture_complete': None, 'study_eligible': False}
