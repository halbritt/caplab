"""Observe the kernel tracer relationship for an independently identified peer."""

import os
from pathlib import Path
import re
import stat

from caplab.task_capture_verify import _require


_NAMESPACES = ('mnt', 'pid', 'user', 'net')


def _proc_text(path):
    with open(path, 'rb') as stream:
        raw = stream.read(65537)
    _require(len(raw) <= 65536, 'proc observation exceeds allowance')
    return raw.decode('ascii')


def _namespaces(pid):
    return {name: os.readlink(f'/proc/{pid}/ns/{name}') for name in _NAMESPACES}


def _trace_identity(path):
    path = Path(path)
    _require(path.is_absolute() and path.parent.resolve() == path.parent,
             'trace parent must be resolved')
    identity = path.lstat()
    _require(stat.S_ISREG(identity.st_mode), 'trace must be a regular file')
    return {'device': identity.st_dev, 'inode': identity.st_ino}


def observe_exec_tracer(peer_pid: int, trace_path: Path, *, expected_tracer_executable: Path) -> dict:
    """Read a paused peer's actual tracer and protected output descriptor.

    The caller authenticates and keeps the peer alive, pins trusted tracer
    bytes, and owns namespace construction, private custody and publication.
    This function neither releases the peer nor launches or stops processes.
    """
    _require(type(peer_pid) is int and peer_pid > 0, 'invalid exec peer PID')
    status = dict(line.split(':', 1) for line in _proc_text(f'/proc/{peer_pid}/status').splitlines()
                  if ':' in line)
    tracer_pid = int(status['TracerPid'].strip())
    _require(tracer_pid > 0, 'exec peer has no tracer')
    supervisor_namespaces, peer_namespaces = _namespaces('self'), _namespaces(peer_pid)
    _require(all(peer_namespaces[name] != supervisor_namespaces[name] for name in _NAMESPACES),
             'exec peer shares supervisor namespace')
    tracer_namespaces = _namespaces(tracer_pid)
    _require(tracer_namespaces == supervisor_namespaces, 'tracer left supervisor namespaces')
    cgroup = _proc_text('/proc/self/cgroup')
    _require(_proc_text(f'/proc/{tracer_pid}/cgroup') == cgroup, 'tracer left supervisor cgroup')
    actual, expected = Path(f'/proc/{tracer_pid}/exe').stat(), Path(expected_tracer_executable).stat()
    _require((actual.st_dev, actual.st_ino) == (expected.st_dev, expected.st_ino),
             'tracer executable differs')
    identity = _trace_identity(trace_path)
    _require(not Path(f'/proc/{peer_pid}/root', str(trace_path).lstrip('/')).exists(),
             'host trace path is exposed to peer')
    matching = []
    with os.scandir(f'/proc/{tracer_pid}/fd') as entries:
        for count, entry in enumerate(entries, 1):
            _require(count <= 128, 'tracer descriptor allowance exceeded')
            try:
                descriptor = entry.stat()
            except FileNotFoundError:
                continue
            if (descriptor.st_dev, descriptor.st_ino) == (identity['device'], identity['inode']):
                matching.append(int(entry.name))
    _require(len(matching) == 1, 'tracer lacks one exact trace descriptor')
    descriptor = matching[0]
    info = dict(line.split(':', 1) for line in _proc_text(f'/proc/{tracer_pid}/fdinfo/{descriptor}').splitlines()
                if ':' in line)
    flags = int(info['flags'].strip(), 8)
    _require(flags & os.O_ACCMODE in (os.O_WRONLY, os.O_RDWR), 'tracer trace descriptor is not writable')
    return {'schema': 'caplab.exec-tracer-observation/v1', 'peer_pid': peer_pid,
            'tracer_pid': tracer_pid, 'supervisor_pid': os.getpid(), 'supervisor_cgroup': cgroup,
            'tracer_cgroup': cgroup, 'supervisor_namespaces': supervisor_namespaces,
            'tracer_namespaces': tracer_namespaces, 'peer_namespaces': peer_namespaces,
            'tracer_executable': {'device': actual.st_dev, 'inode': actual.st_ino},
            'trace_identity': identity, 'trace_descriptor': descriptor,
            'trace_descriptor_flags': flags, 'host_trace_path_exposed': False}


def verify_exec_tracer(observation: dict, trace_path: Path, *, expected_pid: int) -> dict:
    """Check a trusted retained observation; its bytes do not attest their origin.

    The caller supplies an independent observation anchor and authenticated
    PID, plus stable custody. The separate exec inspector verifies trace bytes.
    """
    _require(type(expected_pid) is int and expected_pid > 0, 'invalid exec peer PID')
    _validate_observation(observation)
    _require(observation['schema'] == 'caplab.exec-tracer-observation/v1'
             and observation['peer_pid'] == expected_pid, 'tracer observation peer differs')
    _require(observation['trace_identity'] == _trace_identity(trace_path), 'observed trace identity differs')
    _require(observation['host_trace_path_exposed'] is False, 'recorded host trace path is exposed')
    _require(observation['tracer_cgroup'] == observation['supervisor_cgroup'], 'recorded tracer cgroup differs')
    _require(observation['tracer_namespaces'] == observation['supervisor_namespaces'],
             'recorded tracer namespaces differ')
    _require(all(observation['peer_namespaces'][name] != observation['supervisor_namespaces'][name]
                 for name in _NAMESPACES), 'recorded peer shares supervisor namespace')
    _require(observation['trace_descriptor_flags'] & os.O_ACCMODE in (os.O_WRONLY, os.O_RDWR),
             'recorded trace descriptor is not writable')
    return {'schema': 'caplab.exec-tracer-consistency/v1', 'peer_pid': expected_pid,
            'trace_identity': dict(observation['trace_identity']), 'recorded_tracer_custody_agrees': True,
            'observation_origin_verified': False, 'binding_complete': False,
            'native_capture_complete': None, 'study_eligible': False}


def _validate_observation(observation):
    fields = {'schema', 'peer_pid', 'tracer_pid', 'supervisor_pid', 'supervisor_cgroup',
              'tracer_cgroup', 'supervisor_namespaces', 'tracer_namespaces', 'peer_namespaces',
              'tracer_executable', 'trace_identity', 'trace_descriptor', 'trace_descriptor_flags',
              'host_trace_path_exposed'}
    _require(isinstance(observation, dict) and set(observation) == fields,
             'invalid tracer observation fields')
    for name in ('peer_pid', 'tracer_pid', 'supervisor_pid'):
        _require(type(observation[name]) is int and observation[name] > 0, 'invalid recorded process PID')
    _require(len({observation[name] for name in ('peer_pid', 'tracer_pid', 'supervisor_pid')}) == 3,
             'recorded process identities overlap')
    for name in ('trace_descriptor', 'trace_descriptor_flags'):
        _require(type(observation[name]) is int and observation[name] >= 0, 'invalid recorded descriptor')
    for name in ('tracer_executable', 'trace_identity'):
        value = observation[name]
        _require(isinstance(value, dict) and set(value) == {'device', 'inode'}
                 and type(value['device']) is int and value['device'] >= 0
                 and type(value['inode']) is int and value['inode'] > 0, 'invalid recorded file identity')
    for name in ('tracer_cgroup', 'supervisor_cgroup'):
        value = observation[name]
        _require(isinstance(value, str) and re.fullmatch(r'0::/[^\n\0]*\n', value) is not None,
                 'invalid recorded unified cgroup')
    for name in ('tracer_namespaces', 'supervisor_namespaces', 'peer_namespaces'):
        value = observation[name]
        _require(isinstance(value, dict) and set(value) == set(_NAMESPACES), 'invalid recorded namespaces')
        for namespace, link in value.items():
            _require(isinstance(link, str) and re.fullmatch(namespace + r':\[[1-9][0-9]*\]', link) is not None,
                     'invalid recorded namespace identity')
