#!/usr/bin/env python3
"""Fixed model-free probe; creates one temporary user unit and its own cgroups.

Run with PYTHONPATH=src after authorizing the named local resource effects.
This is not a native launcher, arbitrary-command runner or completeness gate.
"""

import argparse
import array
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import socket
import stat
import struct
import subprocess
import time
import uuid

from caplab.process_capture import capture_process, seal_capture_json
from caplab.task_capture import _Inventory
from caplab.task_capture_verify import _Reader, _inventory, _open


MIB = 1024 * 1024
SCRIPT = Path(__file__).resolve()
MARKER = b'retained marker\x00\xff\n'
MOUNTS = ('/scratch', '/tmp', '/dev/shm')
JOIN = """import os,sys
from pathlib import Path
Path(sys.argv[1], 'cgroup.procs').write_text(str(os.getpid()))
os.execv(sys.argv[2], sys.argv[2:])
"""
HANDOFF = """import array,json,os,socket,sys
with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as channel:
    channel.settimeout(3)
    channel.connect('/control.sock')
    roots = []
    try:
        for path in json.loads(sys.argv[1]):
            roots.append(os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW))
        channel.sendmsg([b'R'], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, array.array('i', roots))])
    finally:
        for root in roots:
            os.close(root)
    if channel.recv(1) != b'1':
        raise RuntimeError('supervisor did not accept retained mount')
os.execv('/usr/bin/python3', ['/usr/bin/python3', '-B', '-c', sys.argv[2], sys.argv[3]])
"""
FIXTURE = r"""import errno,json,subprocess,sys
from pathlib import Path
mode = sys.argv[1]
for directory in ('/scratch', '/tmp', '/dev/shm'):
    Path(directory, 'marker.bin').write_bytes(b'retained marker\x00\xff\n' + directory.encode('ascii'))
if mode in ('memory', 'tmp-memory', 'shm-memory'):
    destination = {'memory': '/scratch', 'tmp-memory': '/tmp', 'shm-memory': '/dev/shm'}[mode]
    with Path(destination, 'payload').open('xb', buffering=0) as f:
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
    for directory in ('/scratch', '/tmp', '/dev/shm'):
        Path(directory, 'control').write_bytes(b'ok')
    refused = []
    for path in ('/other', '/dev/other', '/usr/other', '/proc/self/comm'):
        try:
            Path(path).write_bytes(b'not allowed')
        except OSError as error:
            if error.errno != errno.EROFS:
                raise
            refused.append(path)
        else:
            raise RuntimeError('write escaped declared tmpfs mounts: ' + path)
    print(json.dumps({'refused_readonly_writes': refused}))
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


def mount_coverage(raw):
    """Check the fixed fixture topology, including unexpected nested mounts."""
    mounts = []
    for line in raw.splitlines():
        fields = line.split()
        separator = fields.index('-')
        require(separator >= 6 and len(fields) >= separator + 4, 'invalid mountinfo row')
        mounts.append({'path': fields[4], 'options': fields[5].split(','),
                       'filesystem': fields[separator + 1]})
    by_path = {m['path']: m for m in mounts}
    require(len(by_path) == len(mounts), 'ambiguous stacked fixture mounts')
    writable = {m['path'] for m in mounts if 'rw' in m['options']}
    require(writable == {'/scratch', '/tmp', '/dev/shm'}, 'unexpected writable fixture mounts')
    require(all(by_path[path]['filesystem'] == 'tmpfs' for path in writable),
            'writable fixture mount is not tmpfs')
    require(all(path in by_path and 'ro' in by_path[path]['options']
                for path in ('/', '/usr', '/proc', '/dev/null', '/dev/urandom')),
            'required read-only fixture mount is absent or writable')
    return {'raw': raw, 'mounts': mounts, 'writable_tmpfs': sorted(writable)}


def receive_mount(listener, child):
    descriptors = []
    try:
        channel, _ = listener.accept()
        with channel:
            channel.settimeout(3)
            peer_pid, peer_uid, peer_gid = struct.unpack('3i', channel.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
            data, ancillary, flags, _ = channel.recvmsg(
                1, socket.CMSG_SPACE(len(MOUNTS) * array.array('i').itemsize), socket.MSG_CMSG_CLOEXEC)
            for level, kind, raw in ancillary:
                if level == socket.SOL_SOCKET and kind == socket.SCM_RIGHTS:
                    received = array.array('i')
                    received.frombytes(raw[:len(raw) - len(raw) % received.itemsize])
                    descriptors.extend(received)
            require(data == b'R' and flags & ~socket.MSG_CMSG_CLOEXEC == 0
                    and len(descriptors) == len(MOUNTS), 'invalid mount handoff')
            require(peer_uid == os.getuid() and peer_gid == os.getgid(), 'unexpected mount peer owner')
            membership = Path(f'/proc/{peer_pid}/cgroup').read_text().strip()
            require(membership == '0::/' + str(child.relative_to('/sys/fs/cgroup')), 'mount peer is outside fixture group')
            coverage = mount_coverage(Path(f'/proc/{peer_pid}/mountinfo').read_text())
            identities = []
            for path, descriptor in zip(MOUNTS, descriptors, strict=True):
                info = os.fstat(descriptor); capacity = os.fstatvfs(descriptor)
                named = Path(f'/proc/{peer_pid}/root{path}').stat()
                require(stat.S_ISDIR(info.st_mode)
                        and (info.st_dev, info.st_ino) == (named.st_dev, named.st_ino)
                        and capacity.f_blocks * capacity.f_frsize == 64 * MIB,
                        'received descriptor differs from named bounded mount: ' + path)
                identities.append({'source_root': path, 'source_dev': info.st_dev, 'source_ino': info.st_ino,
                                   'allocated_capacity': capacity.f_blocks * capacity.f_frsize})
            require(len({(i['source_dev'], i['source_ino']) for i in identities}) == len(MOUNTS),
                    'mount handoff aliases a directory')
            listener.close()
            channel.sendall(b'1')
            owned = descriptors[:]
            descriptors.clear()
            return owned, {'peer_pid': peer_pid, 'peer_uid': peer_uid, 'peer_gid': peer_gid,
                           'mounts': identities, 'mount_coverage': coverage}
    finally:
        for descriptor in descriptors:
            os.close(descriptor)


def retain_mount(descriptor, output, identity, bytes_left, entries_left):
    output.mkdir(mode=0o700)
    inventory = _Inventory(output, bytes_left, entries_left)
    inventory.visit(descriptor, '.', '.')
    receipt = {'schema': 'caplab.retained-mount-inventory/v1', 'source_root': identity['source_root'],
        'source_scope': 'fixture namespace; not a host path', 'descriptor_identity': identity,
        'max_retained_bytes': bytes_left, 'max_entries': entries_left,
        'retained_bytes': inventory.retained_bytes, 'entries': sorted(inventory.entries, key=lambda e: e['path'])}
    root_entry = receipt['entries'][0]['source_stat']
    require((root_entry['dev'], root_entry['ino']) == (identity['source_dev'], identity['source_ino']),
            'retained root identity differs from received descriptor')
    digest = seal_capture_json(output, 'inventory.json', receipt)
    return digest, inventory.bytes_left, inventory.entries_left


def verify_retention(root, observation):
    for report in observation['reports']:
        require([i['source_root'] for i in report['inventories']] == list(MOUNTS), 'incomplete retained mount set')
        require([i['source_root'] for i in report['mount_descriptor']['mounts']] == list(MOUNTS),
                'incomplete descriptor identity set')
        bytes_left, entries_left = 40 * MIB, 100
        pressure_mount = {'memory': '/scratch', 'tmp-memory': '/tmp', 'shm-memory': '/dev/shm'}.get(report['mode'])
        for index, (item, identity) in enumerate(zip(report['inventories'], report['mount_descriptor']['mounts'], strict=True)):
            path = item['source_root']
            with _open(None, root / (report['mode'] + '-retained') / str(index), directory=True) as fd:
                receipt = _Reader(200000).receipt(fd, 'inventory.json', item['inventory_sha256'],
                                                 'caplab.retained-mount-inventory/v1')
                require(receipt['descriptor_identity'] == identity, 'retained descriptor identity differs')
                require((receipt['max_retained_bytes'], receipt['max_entries']) == (bytes_left, entries_left),
                        'retained mount allowance differs from combined budget')
                size, count = _inventory(fd, receipt, cwd=path, bytes_left=bytes_left, entries_left=entries_left)
                entries = receipt['entries']
                source = entries[0]['source_stat']
                require((source['dev'], source['ino']) == (identity['source_dev'], identity['source_ino']),
                        'retained root differs from handed-off mount')
                bytes_left -= size
                entries_left -= count
                marker, = [e for e in entries if e['path'] == 'marker.bin']
                expected = MARKER + path.encode('ascii')
                require(marker['kind'] == 'file' and marker['bytes'] == len(expected)
                        and marker['sha256'] == hashlib.sha256(expected).hexdigest(), 'retained marker differs')
                if path == pressure_mount:
                    payload, = [e for e in entries if e['path'] == 'payload']
                    require(payload['kind'] == 'file' and payload['bytes'] > 0, 'partial OOM payload was not retained')
        require(report['retained_bytes'] == 40 * MIB - bytes_left
                and report['retained_entries'] == 100 - entries_left, 'combined retention totals differ')


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
    for mode in ('control', 'memory', 'pids', 'tmp-memory', 'shm-memory'):
        child = group / ('fixture-' + mode)
        child.mkdir()
        descriptors = []
        socket_path = root / (mode + '-control.sock')
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
                '--proc', '/proc', '--dir', '/dev',
                '--ro-bind', '/dev/null', '/dev/null', '--ro-bind', '/dev/urandom', '/dev/urandom',
                '--size', str(64 * MIB), '--tmpfs', '/scratch',
                '--size', str(64 * MIB), '--tmpfs', '/tmp',
                '--size', str(64 * MIB), '--tmpfs', '/dev/shm',
                '--chdir', '/scratch', '--setenv', 'PATH', '/usr/bin:/bin',
                '--ro-bind', str(socket_path), '/control.sock',
                '--remount-ro', '/proc', '--remount-ro', '/',
                '--', '/usr/bin/python3', '-B', '-c', HANDOFF, json.dumps(MOUNTS), FIXTURE, mode]
            command = ['/usr/bin/python3', '-B', '-c', JOIN, str(child), *bwrap]
            intent = {'mode': mode, 'cgroup': str(child), 'command': command, 'before': before}
            seal_capture_json(root, mode + '-intent.json', intent)
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as listener:
                listener.bind(str(socket_path)); socket_path.chmod(0o600)
                listener.listen(1); listener.settimeout(3)
                with ThreadPoolExecutor(max_workers=1) as pool:
                    pending = pool.submit(capture_process, command, cwd=root, environment={'PATH': '/usr/bin:/bin'},
                        output_dir=root / mode, max_stream_bytes=200000, timeout_seconds=10)
                    descriptors, identity = receive_mount(listener, child)
                    process = pending.result(timeout=16)
            after = snapshot(child)
            require(not populated(child), 'fixture must be quiescent before mount retention')
            retained = root / (mode + '-retained'); retained.mkdir(mode=0o700)
            inventories = []
            bytes_left, entries_left = 40 * MIB, 100
            for index, (descriptor, mount) in enumerate(zip(descriptors, identity['mounts'], strict=True)):
                digest, bytes_left, entries_left = retain_mount(
                    descriptor, retained / str(index), mount, bytes_left, entries_left)
                inventories.append({'source_root': mount['source_root'], 'inventory_sha256': digest})
            report = {'mode': mode, 'before': before, 'after': after, 'process': process,
                      'populated_before_cleanup': populated(child), 'inventories': inventories,
                      'retained_bytes': 40 * MIB - bytes_left, 'retained_entries': 100 - entries_left,
                      'mount_descriptor': identity}
            seal_capture_json(root, mode + '-observations.json', report)
            reports.append(report)
        finally:
            for descriptor in descriptors:
                os.close(descriptor)
            socket_path.unlink(missing_ok=True)
            cleanup_group(child)
    seal_capture_json(root, 'observations.json', {
        'schema': 'caplab.cgroup-resource-probe-observations/v4', 'unit': unit,
        'delegated_cgroup': str(group), 'kernel': platform.release(), 'python': platform.python_version(),
        'reports': reports, 'fixture_cgroups_removed': True, 'native_execution': False,
        'capture_complete_claim': False})


def expectations(observation):
    reports = {r['mode']: r for r in observation['reports']}
    require(set(reports) == {'control', 'memory', 'pids', 'tmp-memory', 'shm-memory'}, 'incomplete fixture set')
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
    for mode in ('memory', 'tmp-memory', 'shm-memory'):
        require(reports[mode]['process']['return_code'] != 0 and delta(mode, 'memory_events', 'oom_kill') > 0,
                mode + ' writer did not produce an independently observed OOM kill')
    for report in reports.values():
        coverage = report['mount_descriptor']['mount_coverage']
        require(mount_coverage(coverage['raw']) == coverage, 'recorded mount coverage differs')
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
        '--property=RuntimeMaxSec=60', '--property=OOMPolicy=continue', '--property=KillMode=control-group',
        '--', '/usr/bin/env', '-i', 'PATH=/usr/bin:/bin', 'LANG=C.UTF-8',
        'PYTHONPATH=' + str(SCRIPT.parents[1] / 'src'), '/usr/bin/python3', '-B', str(SCRIPT),
        '--output-root', str(root), '--inside-unit', unit]
    seal_capture_json(root, 'intent.json', {'unit': unit, 'command': command, 'environment': environment,
        'script_sha256': hashlib.sha256(SCRIPT.read_bytes()).hexdigest()})
    try:
        process = capture_process(command, cwd=root, environment=environment,
            output_dir=root / 'service', max_stream_bytes=200000, timeout_seconds=70)
        require(process['return_code'] == 0 and process['streams_complete'], 'service failed; inspect retained streams')
        observation = json.loads((root / 'observations.json').read_bytes())
        expectations(observation)
        verify_retention(root, observation)
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
    seal_capture_json(root, 'verification.json', {'schema': 'caplab.cgroup-resource-probe-verification/v4',
        'unit': unit, 'five_fixture_expectations_passed': True, 'unit_removed': True,
        'retained_files_verified_after_service_exit': True,
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
