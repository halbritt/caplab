"""Observe one direct child's executable in a caller-owned frozen leaf cgroup."""

from contextlib import ExitStack
from dataclasses import dataclass
import os
from pathlib import Path
import re
import stat
import time

from caplab.task_capture_verify import _digest, _identity, _open, _read_file, _require


@dataclass(frozen=True)
class FrozenNativeChildEvidence:
    parent_pid: int
    parent_proc_descriptor: int
    expected_executable: Path
    expected_executable_sha256: str
    max_executable_bytes: int
    max_processes: int


def _kernel_bytes(directory, name):
    return _read_file(directory, name, 65536, retain=True)[0]


def _kernel_fields(directory, name):
    rows = [line.split(None, 1) for line in _kernel_bytes(directory, name).splitlines()]
    _require(all(row for row in rows), 'invalid kernel fields')
    fields = {row[0]: row[1] if len(row) == 2 else b'' for row in rows}
    _require(len(fields) == len(rows), 'duplicate kernel field')
    return fields


def _population(group, limit):
    _require(_kernel_bytes(group, 'cgroup.type') == b'domain\n', 'cgroup must be a domain')
    _require(_kernel_fields(group, 'cgroup.events').get(b'frozen') == b'1', 'cgroup is not frozen')
    _require(_kernel_fields(group, 'cgroup.stat').get(b'nr_descendants') == b'0', 'cgroup must be a leaf')
    rows = _kernel_bytes(group, 'cgroup.procs').splitlines()
    _require(all(re.fullmatch(rb'[1-9][0-9]*', row) for row in rows), 'invalid cgroup process ID')
    pids = sorted(int(row) for row in rows)
    _require(len(pids) == len(set(pids)) and len(pids) <= limit, 'cgroup population differs or exceeds allowance')
    return pids


def _process(directory, pid, membership):
    fields = _kernel_fields(directory, 'status')
    selected = {}
    for key in ('Tgid', 'Pid', 'PPid'):
        raw = fields.get((key + ':').encode(), b'')
        _require(re.fullmatch(rb'[0-9]+', raw) is not None, 'invalid process identity field')
        selected[key] = int(raw)
    _require(selected['Tgid'] == selected['Pid'] == pid, 'candidate is not the expected process leader')
    _require(_kernel_bytes(directory, 'cgroup') == membership, 'process left selected cgroup')
    return selected


def _file_object(info):
    return {'device': info.st_dev, 'inode': info.st_ino}


def _executable_identity(directory):
    # This is the kernel's executable magic link, deliberately followed.
    fd = os.open('exe', os.O_RDONLY | os.O_CLOEXEC | os.O_NONBLOCK, dir_fd=directory)
    try:
        info = os.fstat(fd)
        _require(stat.S_ISREG(info.st_mode), 'process executable is not a regular file')
        return _identity(info)
    finally:
        os.close(fd)


def _inspect_group(group, path, evidence, source_identity):
    membership = ('0::/' + str(path.relative_to('/sys/fs/cgroup')) + '\n').encode()
    population = _population(group, evidence.max_processes)
    _require(evidence.parent_pid in population and os.getpid() not in population, 'parent or supervisor cgroup placement differs')
    parent_path = Path('/proc') / str(evidence.parent_pid)
    parent_identity = _file_object(os.fstat(evidence.parent_proc_descriptor))
    _require(parent_identity == _file_object(parent_path.stat()), 'authenticated parent descriptor differs')
    _process(evidence.parent_proc_descriptor, evidence.parent_pid, membership)
    matches = []
    with ExitStack() as stack:
        for pid in population:
            if pid == evidence.parent_pid:
                continue
            proc = stack.enter_context(_open(None, Path('/proc') / str(pid), directory=True))
            status = _process(proc, pid, membership)
            if status['PPid'] == evidence.parent_pid and _executable_identity(proc) == source_identity:
                matches.append((pid, proc, status))
        _require(len(matches) == 1, 'frozen group lacks exactly one matching direct child')
        pid, proc, status = matches[0]
        _require(_population(group, evidence.max_processes) == population, 'frozen population changed')
        _process(evidence.parent_proc_descriptor, evidence.parent_pid, membership)
        _require(_process(proc, pid, membership) == status and _executable_identity(proc) == source_identity,
                 'selected child changed during observation')
        return {'parent_pid': evidence.parent_pid, 'parent_proc_identity': parent_identity,
                'child_pid': pid, 'child_proc_identity': _file_object(os.fstat(proc)), 'child_status': status,
                'cgroup': {'path': str(path), **_file_object(os.fstat(group)), 'frozen': True,
                           'type': 'domain', 'processes': population}}


def observe_frozen_native_child(cgroup_path: Path, *, evidence: FrozenNativeChildEvidence) -> dict:
    """Borrow an authenticated parent descriptor and observe a stable, frozen group.

    The caller owns freezing/thawing, leaf-population scope, source quiescence,
    parent authentication before release, and exclusion of outside migrations,
    fatal signals and namespace changes. This reader never controls processes.
    """
    started = time.monotonic_ns()
    _require(isinstance(evidence, FrozenNativeChildEvidence), 'invalid frozen child evidence')
    _require(type(evidence.parent_pid) is int and evidence.parent_pid > 0, 'invalid parent PID')
    _require(type(evidence.parent_proc_descriptor) is int and evidence.parent_proc_descriptor >= 0,
             'invalid parent descriptor')
    _require(type(evidence.max_processes) is int and 1 <= evidence.max_processes <= 128, 'invalid process allowance')
    _require(type(evidence.max_executable_bytes) is int and 0 < evidence.max_executable_bytes <= 1024**3,
             'invalid executable allowance')
    _digest(evidence.expected_executable_sha256)
    path, source = Path(cgroup_path), Path(evidence.expected_executable)
    _require(path.is_absolute() and path.resolve() == path and path != Path('/sys/fs/cgroup')
             and path.is_relative_to('/sys/fs/cgroup'), 'cgroup must be a resolved non-root kernel path')
    _require(source.is_absolute() and source.resolve() == source, 'executable source must be resolved')
    with _open(None, path, directory=True) as group, _open(None, source) as executable:
        before = _identity(os.fstat(executable))
        _, size, sha = _read_file(None, source, evidence.max_executable_bytes, retain=False)
        _require(sha == evidence.expected_executable_sha256, 'selected executable hash differs')
        observed = _inspect_group(group, path, evidence, before)
        _require(_identity(os.fstat(executable)) == before == _identity(source.stat()), 'executable source changed')
        _require(_file_object(os.fstat(group)) == _file_object(path.stat()), 'cgroup identity changed')
        _require(_population(group, evidence.max_processes) == observed['cgroup']['processes'],
                 'frozen population changed before return')
        return {'schema': 'caplab.frozen-native-child-observation/v1', **observed,
                'executable': {'source_path': str(source), 'bytes': size, 'sha256': sha,
                               **_file_object(os.fstat(executable))},
                'started_monotonic_ns': started, 'finished_monotonic_ns': time.monotonic_ns(),
                'live_child_executable_observed': True, 'continuous_image_residence_verified': False,
                'trace_linked': False, 'task_success_verified': False, 'binding_complete': False,
                'native_capture_complete': None, 'study_eligible': False}
