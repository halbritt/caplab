"""Inspect bounded supervisor-owned strace exec evidence, without attesting its origin."""

from pathlib import Path
import re

from caplab.task_capture_verify import _digest, _read_file, _require
from caplab.process_trace import _creation_records


_STRING = r'"(?:\\x[0-9a-f]{2})*"'
_ARRAY = r'\[(?:' + _STRING + r'(?:, ' + _STRING + r')*)?\]'
_EXEC = re.compile(r'execve\((' + _STRING + r'), (' + _ARRAY + r'), (' + _ARRAY +
                   r')\)[ \t]+= (0|-1 [A-Z][A-Z0-9_]* \([^\r\n]*\))')


def _decode(value):
    return bytes.fromhex(value[1:-1].replace('\\x', ''))


def _array(value):
    return [_decode(item) for item in re.findall(_STRING, value)]


def _text(value):
    _require(isinstance(value, str) and '\0' not in value, 'invalid expected execution string')
    try:
        return value.encode('utf-8')
    except UnicodeError as error:
        raise ValueError('expected execution string must be UTF-8') from error


def inspect_exec_trace(trace_path: Path, *, expected_trace_sha256: str, expected_pid: int,
                       expected_executable: str, expected_command: list[str],
                       expected_environment: dict[str, str], max_trace_bytes: int) -> dict:
    """Require one exact successful execve for a caller-identified PID.

    The caller owns trace provenance, process identity/lifetime, isolated
    custody and the expected invocation. A byte anchor alone proves none of
    those. Inputs are borrowed; only the bounded read descriptor is owned.
    """
    _digest(expected_trace_sha256)
    _require(type(expected_pid) is int and expected_pid > 0 and
             type(max_trace_bytes) is int and max_trace_bytes > 0, 'invalid exec trace identity or allowance')
    executable = _text(expected_executable)
    _require(executable.startswith(b'/') and isinstance(expected_command, list) and expected_command,
             'expected executable must be absolute and argv nonempty')
    command = [_text(item) for item in expected_command]
    _require(command[0] and isinstance(expected_environment, dict), 'invalid expected argv or environment')
    environment = {}
    for key, value in expected_environment.items():
        encoded_key = _text(key)
        _require(encoded_key and b'=' not in encoded_key, 'invalid expected environment key')
        environment[encoded_key] = _text(value)
    path = Path(trace_path)
    _require(path.is_absolute() and path.parent.resolve() == path.parent, 'trace parent must be resolved')
    raw, size, sha = _read_file(None, path, max_trace_bytes, retain=True)
    _require(sha == expected_trace_sha256, 'exec trace hash differs')
    _require(raw.endswith(b'\n'), 'exec trace has incomplete final line')
    try:
        lines = raw.decode('ascii').splitlines()
    except UnicodeError as error:
        raise ValueError('exec trace must use ASCII hex format') from error
    prefix = re.compile(str(expected_pid) + r'\s+(.+)')
    _, creation_lines = _creation_records(lines, selected_pid=expected_pid)
    pending, successes, observed_calls = None, [], 0
    for number, line in enumerate(lines, 1):
        selected = prefix.fullmatch(line)
        if selected is None:
            continue
        if number in creation_lines:
            _require(pending is None, 'exec trace overlaps process creation')
            continue
        body = selected[1]
        if body.startswith('<... execve resumed>'):
            _require(pending is not None, 'exec trace resumes without entry')
            start, partial = pending
            body = partial + body[len('<... execve resumed>'):]
            pending = None
        elif body.startswith('execve('):
            _require(pending is None, 'exec trace overlaps calls for one PID')
            start = number
            if body.endswith(' <unfinished ...>'):
                pending = (start, body[:-len(' <unfinished ...>')])
                continue
        else:
            _require(body.startswith(('--- ', '+++ ')), 'unsupported selected-PID trace record')
            continue
        parsed = _EXEC.fullmatch(body)
        _require(parsed is not None, 'unsupported or abbreviated execve record')
        observed_calls += 1
        name, argv, envp, result = parsed.groups()
        if _decode(name) != executable or result != '0':
            continue
        observed_environment = {}
        for entry in _array(envp):
            key, separator, value = entry.partition(b'=')
            _require(separator and key and key not in observed_environment, 'invalid or duplicate execution environment key')
            observed_environment[key] = value
        _require(_array(argv) == command and observed_environment == environment, 'executed argv or environment differs')
        successes.append({'entry_line': start, 'completion_line': number})
    _require(pending is None, 'exec trace ends with an unfinished selected-PID call')
    _require(len(successes) == 1, 'expected exactly one successful matching execve')
    return {'schema': 'caplab.exec-trace-inspection/v1', 'trace_sha256': sha, 'trace_bytes': size,
            'pid': expected_pid, 'executable': expected_executable, 'matching_execve': successes[0],
            'observed_pid_execve_calls': observed_calls, 'successful_execve_agrees': True,
            'trace_provenance_verified': False, 'binding_complete': False,
            'native_capture_complete': None, 'study_eligible': False}
