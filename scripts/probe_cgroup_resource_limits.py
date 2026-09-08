#!/usr/bin/env python3
"""Fixed model-free probe; creates one temporary user unit and its own cgroups.

Run with PYTHONPATH=src after authorizing the named local resource effects.
This is not a native launcher, arbitrary-command runner or completeness gate.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import time
import uuid

from caplab.process_capture import capture_process, seal_capture_json


MIB = 1024 * 1024
SCRIPT = Path(__file__).resolve()
JOIN = """import os,sys
from pathlib import Path
Path(sys.argv[1], 'cgroup.procs').write_text(str(os.getpid()))
os.execv(sys.argv[2], sys.argv[2:])
"""
FIXTURE = """import errno,json,subprocess,sys
from pathlib import Path
mode = sys.argv[1]
if mode == 'memory':
    with Path('/scratch/payload').open('xb', buffering=0) as f:
        for _ in range(64):
            if f.write(b'x' * 1048576) != 1048576:
                raise RuntimeError('short fixture write')
elif mode == 'pids':
    children = []
    caught = None
    try:
        for _ in range(32):
            try:
                children.append(subprocess.Popen(['/usr/bin/sleep', '2']))
            except OSError as error:
                if error.errno != errno.EAGAIN:
                    raise
                caught = error.errno
                break
    finally:
        for child in children:
            child.terminate()
        for child in children:
            child.wait(timeout=3)
    print(json.dumps({'caught_errno': caught, 'children': len(children)}))
elif mode == 'control':
    Path('/scratch/control').write_bytes(b'ok')
else:
    raise ValueError('unknown fixed fixture')
print('fixture exits successfully')
"""


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def counters(path):
    raw = path.read_text(encoding='ascii')
    pairs = [line.split() for line in raw.splitlines()]
    require(all(len(p) == 2 and p[1].isdigit() for p in pairs), 'invalid kernel counters')
    values = {key: int(value) for key, value in pairs}
    require(len(values) == len(pairs), 'duplicate kernel counter')
    return {'raw': raw, 'values': values}


def snapshot(group):
    names = ('memory.max', 'memory.swap.max', 'memory.oom.group', 'memory.current', 'pids.max', 'pids.current')
    return {'limits_and_usage': {name: (group / name).read_text().strip() for name in names},
            'memory_events': counters(group / 'memory.events'),
            'pids_events': counters(group / 'pids.events'),
            'cgroup_events': counters(group / 'cgroup.events')}


def populated(group):
    return counters(group / 'cgroup.events')['values']['populated'] != 0


def cleanup_group(group):
    if populated(group):
        (group / 'cgroup.kill').write_text('1')
    deadline = time.monotonic() + 3
    while populated(group) and time.monotonic() < deadline:
        time.sleep(0.02)
    require(not populated(group), 'owned fixture cgroup did not empty')
    group.rmdir()


def inside(root, unit):
    require(re.fullmatch(r'caplab-resource-probe-[0-9a-f]{32}\.service', unit), 'invalid probe unit')
    membership = Path('/proc/self/cgroup').read_text().strip()
    require(membership.startswith('0::/') and '\n' not in membership, 'unified cgroup required')
    current = Path('/sys/fs/cgroup') / membership[3:].lstrip('/')
    require(current.name == 'supervisor' and current.parent.name == unit,
            'probe must run in its generated unit supervisor subgroup')
    group = current.parent
    require((group / 'memory.max').read_text().strip() == str(128 * MIB), 'outer memory limit differs')
    require((group / 'memory.swap.max').read_text().strip() == '0', 'outer swap limit differs')
    require((group / 'pids.max').read_text().strip() == '64', 'outer task limit differs')
    (group / 'cgroup.subtree_control').write_text('+memory +pids')
    reports = []
    for mode in ('control', 'memory', 'pids'):
        child = group / ('fixture-' + mode)
        child.mkdir()
        try:
            limits = {'memory.max': str(32 * MIB), 'memory.swap.max': '0',
                      'memory.oom.group': '1', 'pids.max': '8' if mode == 'pids' else '16'}
            for name, value in limits.items():
                (child / name).write_text(value)
            before = snapshot(child)
            require(all(before['limits_and_usage'][k] == v for k, v in limits.items()),
                    'fixture limits differ; refusing launch')
            require(not populated(child), 'fixture group is not empty before launch')
            bwrap = ['/usr/bin/bwrap', '--unshare-all', '--die-with-parent', '--new-session', '--clearenv',
                '--ro-bind', '/usr', '/usr', '--symlink', 'usr/bin', '/bin',
                '--symlink', 'usr/lib', '/lib', '--symlink', 'usr/lib64', '/lib64',
                '--proc', '/proc', '--dev', '/dev', '--size', str(64 * MIB), '--tmpfs', '/scratch',
                '--chdir', '/scratch', '--setenv', 'PATH', '/usr/bin:/bin',
                '--', '/usr/bin/python3', '-B', '-c', FIXTURE, mode]
            command = ['/usr/bin/python3', '-B', '-c', JOIN, str(child), *bwrap]
            intent = {'mode': mode, 'cgroup': str(child), 'command': command, 'before': before}
            seal_capture_json(root, mode + '-intent.json', intent)
            process = capture_process(command, cwd=root, environment={'PATH': '/usr/bin:/bin'},
                output_dir=root / mode, max_stream_bytes=200000, timeout_seconds=10)
            after = snapshot(child)
            report = {'mode': mode, 'before': before, 'after': after, 'process': process,
                      'populated_before_cleanup': populated(child)}
            seal_capture_json(root, mode + '-observations.json', report)
            reports.append(report)
        finally:
            cleanup_group(child)
    seal_capture_json(root, 'observations.json', {
        'schema': 'caplab.cgroup-resource-probe-observations/v1', 'unit': unit,
        'delegated_cgroup': str(group), 'kernel': platform.release(), 'python': platform.python_version(),
        'reports': reports, 'fixture_cgroups_removed': True, 'native_execution': False,
        'capture_complete_claim': False})


def expectations(observation):
    reports = {r['mode']: r for r in observation['reports']}
    require(set(reports) == {'control', 'memory', 'pids'}, 'incomplete fixture set')
    require(all(not r['populated_before_cleanup'] for r in reports.values()), 'residual fixture processes')
    require(all(r['process']['streams_complete'] and r['process']['termination'] == 'exited'
                for r in reports.values()), 'incomplete fixture process capture')
    def delta(mode, family, key):
        r = reports[mode]
        return r['after'][family]['values'][key] - r['before'][family]['values'][key]
    control = reports['control']
    require(control['process']['return_code'] == 0 and control['process']['streams_complete'], 'control failed')
    require(delta('control', 'memory_events', 'oom') == 0 and delta('control', 'pids_events', 'max') == 0,
            'control encountered a resource event')
    require(reports['memory']['process']['return_code'] != 0 and delta('memory', 'memory_events', 'oom_kill') > 0,
            'tmpfs writer did not produce an independently observed OOM kill')
    require(reports['pids']['process']['return_code'] == 0 and delta('pids', 'pids_events', 'max') > 0,
            'caught fork failure did not retain independent task-limit evidence')


def run(root):
    require(root.is_absolute() and root.parent.resolve() == root.parent and not root.exists(),
            'output root must be fresh with an absolute resolved parent')
    root.mkdir(mode=0o700)
    unit = 'caplab-resource-probe-' + uuid.uuid4().hex + '.service'
    environment = {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8',
                   'XDG_RUNTIME_DIR': f'/run/user/{os.getuid()}',
                   'DBUS_SESSION_BUS_ADDRESS': f'unix:path=/run/user/{os.getuid()}/bus'}
    command = ['/usr/bin/systemd-run', '--user', '--unit=' + unit, '--wait', '--pipe', '--collect',
        '--service-type=exec', '--property=Delegate=memory pids', '--property=DelegateSubgroup=supervisor',
        '--property=MemoryMax=134217728', '--property=MemorySwapMax=0', '--property=TasksMax=64',
        '--property=RuntimeMaxSec=30', '--property=OOMPolicy=continue', '--property=KillMode=control-group',
        '--', '/usr/bin/env', '-i', 'PATH=/usr/bin:/bin', 'LANG=C.UTF-8',
        'PYTHONPATH=' + str(SCRIPT.parents[1] / 'src'), '/usr/bin/python3', '-B', str(SCRIPT),
        '--output-root', str(root), '--inside-unit', unit]
    seal_capture_json(root, 'intent.json', {'unit': unit, 'command': command, 'environment': environment,
        'script_sha256': hashlib.sha256(SCRIPT.read_bytes()).hexdigest()})
    try:
        process = capture_process(command, cwd=root, environment=environment,
            output_dir=root / 'service', max_stream_bytes=200000, timeout_seconds=40)
        require(process['return_code'] == 0 and process['streams_complete'], 'service failed; inspect retained streams')
        observation = json.loads((root / 'observations.json').read_bytes())
        expectations(observation)
    finally:
        # Exact generated unit only. No broad service, cgroup or process cleanup.
        cleanup = subprocess.run(['/usr/bin/systemctl', '--user', 'stop', unit], env=environment,
                                 capture_output=True, timeout=5)
        state = subprocess.run(['/usr/bin/systemctl', '--user', 'show', unit, '--property=LoadState', '--value'],
                               env=environment, capture_output=True, timeout=5)
        seal_capture_json(root, 'cleanup.json', {'unit': unit, 'stop_return_code': cleanup.returncode,
            'stop_stdout': cleanup.stdout.decode(), 'stop_stderr': cleanup.stderr.decode(),
            'show_return_code': state.returncode, 'load_state': state.stdout.decode().strip(),
            'show_stderr': state.stderr.decode()})
        require(state.stdout.strip() == b'not-found', 'generated transient unit remains loaded')
    require(not Path(observation['delegated_cgroup']).exists(), 'generated cgroup remains after unit cleanup')
    seal_capture_json(root, 'verification.json', {'schema': 'caplab.cgroup-resource-probe-verification/v1',
        'unit': unit, 'three_fixture_expectations_passed': True, 'unit_removed': True,
        'native_execution': False, 'capture_complete_claim': False})
    print(json.dumps({'output_root': str(root), 'unit': unit, 'verified': True}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root', type=Path, required=True)
    parser.add_argument('--inside-unit', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.inside_unit:
        inside(args.output_root, args.inside_unit)
    else:
        run(args.output_root)


if __name__ == '__main__':
    main()
