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
import shutil
import socket
import stat
import struct
import subprocess
import time
import uuid

from caplab.process_capture import capture_process, seal_capture_json
from caplab.capture_accounting import build_capture_byte_report
from caplab.capture_quarantine import check_capture_bytes, check_capture_document
from caplab.codex_capture_link import link_codex_final_message, link_codex_root
from caplab.native_capture_invocation import NativeCaptureContext, build_native_capture_invocation
from caplab.native_collection import NativeRuntimeDescriptor, collect_native_outputs
from caplab.native_collection_verify import verify_native_collection
from caplab.native_runtime import prepare_native_runtime
from caplab.native_tool_pairs import inspect_captured_tool_pairs
from caplab.supervised_task_capture import SupervisedTaskCapture
from caplab.task_capture import TaskCaptureLimits, _Inventory
from caplab.task_capture_verify import _Reader, _inventory, _open


MIB = 1024 * 1024
SCRIPT = Path(__file__).resolve()
MARKER = b'retained marker\x00\xff\n'
MOUNTS = ('/scratch', '/tmp', '/dev/shm', '/work', '/episode')
POLICY = SCRIPT.parent.parent / 'docs/product/contracts/native-agent-systems.json'
ROOT_ID = 'resource-fixture'
JOIN = """import os,sys
from pathlib import Path
Path(sys.argv[1], 'cgroup.procs').write_text(str(os.getpid()))
os.execv(sys.argv[2], sys.argv[2:])
"""
HANDOFF = """import array,json,os,socket,sys
from pathlib import Path
Path('/work/item').write_bytes(b'old')
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
os.execv('/usr/bin/python3', ['/usr/bin/python3', '-B', '-c', *sys.argv[2:]])
"""
FIXTURE = r"""import errno,json,subprocess,sys
from pathlib import Path
mode = sys.argv[1]
config = json.loads(sys.argv[2])
def emit(event):
    print(json.dumps(event), flush=True)
def append(event):
    with session.open('a') as stream:
        stream.write(json.dumps(event) + '\n')
paths = config['capture_locations']
session = Path(paths['session_search_root']) / ('rollout-2026-09-08T12-00-00-' + config['root_id'] + '.jsonl')
session.parent.mkdir(parents=True)
append({'type':'session_meta','payload':{'id':config['root_id'],'cli_version':'synthetic-resource-fixture'}})
append({'type':'turn_context','payload':{'model':'gpt-5.6-terra','effort':'max'}})
diagnostic = Path(paths['diagnostic_search_root']) / 'raw'
diagnostic.parent.mkdir(parents=True)
diagnostic.write_bytes(b'\x00\xfffixture began\n')
emit({'type':'thread.started','thread_id':config['root_id']})
emit({'type':'turn.started'})
emit({'type':'item.started','item':{'id':'work','type':'command_execution','command':mode}})
Path('/work/item').write_bytes(b'changed')
for directory in config['mounts']:
    Path(directory, 'marker.bin').write_bytes(b'retained marker\x00\xff\n' + directory.encode('ascii'))
if mode in ('memory', 'tmp-memory', 'shm-memory'):
    destination = {'memory': '/scratch', 'tmp-memory': '/tmp', 'shm-memory': '/dev/shm'}[mode]
    with Path(destination, 'payload').open('xb', buffering=0) as f:
        for _ in range(64):
            if f.write(b'x' * 1048576) != 1048576:
                raise RuntimeError('short fixture write')
    result = {'pressure_exhausted_without_oom': True}
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
    result = {'caught_errno': caught, 'children': len(children)}
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
    result = {'refused_readonly_writes': refused}
else:
    raise ValueError('unknown fixed fixture')
emit({'type':'item.completed','item':{'id':'work','type':'command_execution',
    'status':'completed','exit_code':0,'aggregated_output':json.dumps(result)}})
message = 'synthetic fixture completed'
Path(paths['final_message']).write_text(message)
append({'type':'event_msg','payload':{'type':'agent_message','message':message}})
emit({'type':'item.completed','item':{'id':'final','type':'agent_message','text':message}})
emit({'type':'turn.completed'})
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


def mount_coverage(raw, *, usable_devices=False, nested_userns=False):
    """Check the fixed fixture topology, including unexpected nested mounts."""
    require(type(nested_userns) is bool, 'nested_userns must be a boolean')
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
    devices = {'/dev/null', '/dev/urandom'} if usable_devices else set()
    procfs = {'/proc'} if nested_userns else set()
    require(writable == set(MOUNTS) | devices | procfs, 'unexpected writable fixture mounts')
    require(all(by_path[path]['filesystem'] == 'tmpfs' for path in MOUNTS),
            'writable fixture mount is not tmpfs')
    require(all(by_path[path]['filesystem'] == 'devtmpfs' and 'nodev' not in by_path[path]['options']
                for path in devices), 'device mount does not allow device access')
    readonly = ('/', '/usr') + (() if nested_userns else ('/proc',)) + (() if usable_devices else ('/dev/null', '/dev/urandom'))
    require(all(path in by_path and 'ro' in by_path[path]['options']
                for path in readonly),
            'required read-only fixture mount is absent or writable')
    if nested_userns:
        require(by_path['/proc']['filesystem'] == 'proc', 'nested procfs has wrong filesystem')
        require(not any(m['path'].startswith('/proc/') for m in mounts), 'nested procfs has covered paths')
        require({'nosuid', 'nodev', 'noexec'} <= set(by_path['/proc']['options']), 'nested procfs lacks mount protections')
    return {'raw': raw, 'mounts': mounts, 'writable_tmpfs': sorted(MOUNTS),
            **({'writable_procfs': ['/proc']} if nested_userns else {}),
            **({'writable_devices': sorted(devices)} if usable_devices else {})}


def verify_nested_procfs(observation):
    """Validate recorded namespace and privilege predicates, not live safety."""
    require(isinstance(observation, dict) and observation.get('schema') == 'caplab.nested-procfs/v1',
            'missing nested procfs observation')
    namespaces = observation.get('namespaces')
    require(isinstance(namespaces, dict) and set(namespaces) == {'pid', 'mnt', 'net', 'user'},
            'incomplete nested procfs namespaces')
    for name, pair in namespaces.items():
        require(isinstance(pair, dict) and set(pair) == {'supervisor', 'peer'}, 'invalid namespace pair')
        require(all(isinstance(value, str) and re.fullmatch(name + r':\[[0-9]+\]', value)
                    for value in pair.values()), 'invalid namespace identity')
        require(pair['supervisor'] != pair['peer'], 'nested procfs shares supervisor namespace')
    require(observation.get('proc_pid1_namespace') == namespaces['pid']['peer'],
            'procfs does not show the peer PID namespace')
    status = observation.get('status')
    require(isinstance(status, dict) and set(status) == {'CapEff', 'CapPrm', 'CapInh', 'CapAmb', 'NoNewPrivs'},
            'incomplete nested procfs privilege observation')
    require(all(status[name] == '0000000000000000' for name in ('CapEff', 'CapPrm', 'CapInh', 'CapAmb'))
            and status['NoNewPrivs'] == '1', 'nested procfs peer retains privileges')


def inspect_nested_procfs(peer_pid):
    """Inspect the paused peer before allowing writable per-process controls."""
    namespaces = {name: {'supervisor': os.readlink('/proc/self/ns/' + name),
                         'peer': os.readlink(f'/proc/{peer_pid}/ns/{name}')}
                  for name in ('pid', 'mnt', 'net', 'user')}
    require(all(pair['supervisor'] != pair['peer'] for pair in namespaces.values()),
            'nested procfs shares supervisor namespace')
    status = dict(line.split(':', 1) for line in Path(f'/proc/{peer_pid}/status').read_text().splitlines()
                  if ':' in line)
    observation = {'schema': 'caplab.nested-procfs/v1', 'namespaces': namespaces,
                   'proc_pid1_namespace': os.readlink(f'/proc/{peer_pid}/root/proc/1/ns/pid'),
                   'status': {name: status.get(name, '').strip()
                              for name in ('CapEff', 'CapPrm', 'CapInh', 'CapAmb', 'NoNewPrivs')}}
    verify_nested_procfs(observation)
    return observation


def inspect_devices(peer_pid):
    devices = []
    for name in ('null', 'urandom'):
        path = Path(f'/proc/{peer_pid}/root/dev/{name}')
        info, host = path.stat(), Path('/dev', name).stat()
        require(stat.S_ISCHR(info.st_mode) and info.st_rdev == host.st_rdev, 'peer device identity differs')
        fd = os.open(path, os.O_RDWR if name == 'null' else os.O_RDONLY)
        try:
            read_count = len(os.read(fd, 1))
            require(read_count == (0 if name == 'null' else 1), 'device read differs')
            if name == 'null':
                require(os.write(fd, b'probe') == 5, 'null device did not discard write')
        finally:
            os.close(fd)
        devices.append({'path': '/dev/' + name, 'rdev': info.st_rdev, 'read_bytes': read_count,
                        'null_write_verified': name == 'null'})
    return devices


def receive_mount(listener, child, recorder, *, inspect_peer=None, usable_devices=False, quarantine_factory=None,
                  nested_userns=False):
    require(type(nested_userns) is bool, 'nested_userns must be a boolean')
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
            coverage = mount_coverage(Path(f'/proc/{peer_pid}/mountinfo').read_text(), usable_devices=usable_devices,
                                      nested_userns=nested_userns)
            procfs = inspect_nested_procfs(peer_pid) if nested_userns else None
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
            peer_checks = inspect_peer(peer_pid) if inspect_peer is not None else None
            device_access = inspect_devices(peer_pid) if usable_devices else None
            index = MOUNTS.index('/work')
            task = identities[index]
            before_hash = recorder.capture_before(descriptors[index],
                expected_device=task['source_dev'], expected_inode=task['source_ino'])
            identity = {'peer_pid': peer_pid, 'peer_uid': peer_uid, 'peer_gid': peer_gid,
                        'mounts': identities, 'mount_coverage': coverage,
                        'before_inventory_sha256': before_hash}
            if inspect_peer is not None:
                identity['peer_checks'] = peer_checks
            if usable_devices:
                identity['device_access'] = device_access
            if nested_userns:
                identity['nested_procfs'] = procfs
            name = child.name.removeprefix('fixture-') + '-handoff.json'
            for path in (recorder.output_dir.parent / name,
                         recorder.output_dir.parent / ('.' + name.removesuffix('.json') + '.pending')):
                check_capture_bytes(quarantine_factory, os.fsencode(path))
            check_capture_document(quarantine_factory, identity)
            seal_capture_json(recorder.output_dir.parent, name, identity)
            listener.close()
            channel.sendall(b'1')
            owned = descriptors[:]
            descriptors.clear()
            return owned, identity
    finally:
        for descriptor in descriptors:
            os.close(descriptor)


def retain_mount(descriptor, output, identity, bytes_left, entries_left, *, quarantine_factory=None):
    """Retain one quiescent borrowed mount; the caller owns policy and authorization."""
    identity = dict(identity)
    if quarantine_factory is not None:
        for path in (output, output / 'inventory.json', output / '.inventory.pending'):
            check_capture_bytes(quarantine_factory, os.fsencode(path))
        check_capture_bytes(quarantine_factory, os.fsencode(identity['source_root']))
        check_capture_document(quarantine_factory, identity)
    output.mkdir(mode=0o700)
    inventory = _Inventory(output, bytes_left, entries_left, quarantine_factory)
    inventory.visit(descriptor, '.', '.')
    receipt = {'schema': 'caplab.retained-mount-inventory/v1', 'source_root': identity['source_root'],
        'source_scope': 'fixture namespace; not a host path', 'descriptor_identity': identity,
        'max_retained_bytes': bytes_left, 'max_entries': entries_left,
        'retained_bytes': inventory.retained_bytes, 'entries': sorted(inventory.entries, key=lambda e: e['path'])}
    root_entry, = [entry['source_stat'] for entry in receipt['entries'] if entry['path'] == '.']
    require((root_entry['dev'], root_entry['ino']) == (identity['source_dev'], identity['source_ino']),
            'retained root identity differs from received descriptor')
    check_capture_document(quarantine_factory, receipt)
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
                source, = [entry['source_stat'] for entry in entries if entry['path'] == '.']
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


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_captures(root, report):
    """Rebuild derived checks from retained bundles after source namespace exit."""
    attempt = root / report['mode']
    collection = root / (report['mode'] + '-collection')
    anchors = report['capture_anchors']
    options = dict(task_custody=attempt, collection_custody=collection,
        expected_attempt_sha256=anchors['attempt_sha256'],
        expected_collection_sha256=anchors['collection_sha256'], max_receipt_bytes=200000)
    native = verify_native_collection(POLICY, collection,
        expected_collection_sha256=anchors['collection_sha256'], max_receipt_bytes=200000)
    linked = link_codex_root(POLICY, **options, max_identity_bytes=100000)
    accounting = build_capture_byte_report(POLICY, **options)
    pairs = inspect_captured_tool_pairs(attempt, expected_attempt_sha256=anchors['attempt_sha256'],
        format='codex-exec-jsonl', expected_root_id=ROOT_ID, max_receipt_bytes=200000, max_event_bytes=100000)
    task = pairs['task_capture']
    require(digest(root / (report['mode'] + '-handoff.json')) == anchors['handoff_sha256']
            and json.loads((root / (report['mode'] + '-handoff.json')).read_bytes()) == report['mount_descriptor'],
            'handoff differs from pre-release custody')
    identities = {m['source_root']: m for m in report['mount_descriptor']['mounts']}
    for source, name in ((task['task_source'], '/work'), (native['runtime_source'], '/episode')):
        identity = identities[name]
        require((source['namespace_root'], source['device'], source['inode']) ==
                (name, identity['source_dev'], identity['source_ino']), 'capture source differs from handoff')
    captured_attempt = json.loads((attempt / 'attempt.json').read_bytes())
    require(captured_attempt['before_inventory_sha256'] == report['mount_descriptor']['before_inventory_sha256'],
            'before inventory differs from pre-release anchor')
    require(captured_attempt['process'] == report['process'], 'resource and task process receipts differ')
    collected = json.loads((collection / 'collection.json').read_bytes())
    diagnostic, = [e for e in collected['entries'] if e['path'] == 'diagnostic_search_root/raw']
    require((collection / 'objects' / diagnostic['object']).read_bytes() == b'\x00\xfffixture began\n',
            'retained diagnostic bytes differ')
    for phase, expected in (('before', b'old'), ('after', b'changed')):
        inventory = json.loads((attempt / phase / 'inventory.json').read_bytes())
        entry, = [e for e in inventory['entries'] if e['path'] == 'item']
        require((attempt / phase / entry['object']).read_bytes() == expected, 'retained task bytes differ')
    require(pairs['tool_pairs_available'], 'authored tool events unavailable')
    failed = report['mode'] in ('memory', 'tmp-memory', 'shm-memory')
    expected_counts = {'request_without_result': 1} if failed else {'paired': 1}
    require(pairs['tool_pair_report']['status_counts'] == expected_counts, 'tool lifecycle missingness differs')
    require(native['missing_locations'] == (['final_message'] if failed else []), 'final output missingness differs')
    final = None if failed else link_codex_final_message(POLICY, **options, max_identity_bytes=100000)
    require(linked['executed_invocation_bound'] is False and linked['native_capture_complete'] is None,
            'fixture must not assert native execution or completeness')
    return {'native': native, 'root_link': linked, 'final_link': final, 'accounting': accounting, 'pairs': pairs,
            'native_execution': False, 'capture_complete_claim': False}


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
            task = root / (mode + '-task'); task.mkdir(mode=0o700)
            (task / 'item').write_bytes(b'old')
            plan = build_native_capture_invocation(POLICY, 'codex-terra-max',
                context=NativeCaptureContext('/work', '/episode', b'synthetic resource fixture', None))
            prepared = root / (mode + '-prepared')
            prepare_native_runtime(POLICY, plan, expected_invocation_sha256=plan['invocation_sha256'],
                                   task_root=task, output_dir=prepared)
            preparation_hash = digest(prepared / 'preparation.json')
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
                '--dev-bind', '/dev/null', '/dev/null', '--dev-bind', '/dev/urandom', '/dev/urandom',
                '--size', str(64 * MIB), '--tmpfs', '/scratch',
                '--size', str(64 * MIB), '--tmpfs', '/tmp',
                '--size', str(64 * MIB), '--tmpfs', '/dev/shm',
                '--size', str(64 * MIB), '--tmpfs', '/work',
                '--size', str(64 * MIB), '--tmpfs', '/episode',
                '--chdir', '/work', '--setenv', 'PATH', '/usr/bin:/bin',
                '--ro-bind', str(socket_path), '/control.sock',
                '--remount-ro', '/proc', '--remount-ro', '/',
                '--', '/usr/bin/python3', '-B', '-c', HANDOFF, json.dumps(MOUNTS), FIXTURE, mode,
                json.dumps({'capture_locations': plan['capture_locations'], 'root_id': ROOT_ID, 'mounts': MOUNTS})]
            command = ['/usr/bin/python3', '-B', '-c', JOIN, str(child), *bwrap]
            intent = {'mode': mode, 'cgroup': str(child), 'command': command, 'before': before}
            seal_capture_json(root, mode + '-intent.json', intent)
            with SupervisedTaskCapture(command, task_root=task, namespace_root='/work',
                    environment={'PATH': '/usr/bin:/bin'}, output_dir=root / mode,
                    limits=TaskCaptureLimits(200000, 10000, 100, 10), max_process_receipt_bytes=20000) as recorder:
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as listener:
                    listener.bind(str(socket_path)); socket_path.chmod(0o600)
                    listener.listen(1); listener.settimeout(3)
                    with ThreadPoolExecutor(max_workers=1) as pool:
                        pending = pool.submit(capture_process, command, cwd=task, environment={'PATH': '/usr/bin:/bin'},
                            output_dir=root / mode / 'process', max_stream_bytes=200000, timeout_seconds=10)
                        descriptors, identity = receive_mount(listener, child, recorder, usable_devices=True)
                        process = pending.result(timeout=16)
                after = snapshot(child)
                seal_capture_json(root, mode + '-resource-exit.json',
                    {'before': before, 'after': after, 'process': process, 'populated': populated(child)})
                require(not populated(child), 'fixture must be quiescent before task and native retention')
                recorder.finish(expected_process_sha256=digest(root / mode / 'process/capture.json'))
                index = MOUNTS.index('/episode'); runtime = identity['mounts'][index]
                collect_native_outputs(POLICY, prepared, expected_preparation_sha256=preparation_hash,
                    output_dir=root / (mode + '-collection'), max_receipt_bytes=100000,
                    max_artifact_bytes=100000, max_entries=100,
                    runtime_descriptor=NativeRuntimeDescriptor(descriptors[index], runtime['source_dev'], runtime['source_ino']))
            retained = root / (mode + '-retained'); retained.mkdir(mode=0o700)
            inventories = []
            bytes_left, entries_left = 40 * MIB, 100
            for index, (descriptor, mount) in enumerate(zip(descriptors, identity['mounts'], strict=True)):
                inventory_hash, bytes_left, entries_left = retain_mount(
                    descriptor, retained / str(index), mount, bytes_left, entries_left)
                inventories.append({'source_root': mount['source_root'], 'inventory_sha256': inventory_hash})
            report = {'mode': mode, 'before': before, 'after': after, 'process': process,
                      'populated_before_cleanup': populated(child), 'inventories': inventories,
                      'retained_bytes': 40 * MIB - bytes_left, 'retained_entries': 100 - entries_left,
                      'mount_descriptor': identity,
                      'capture_anchors': {'attempt_sha256': digest(root / mode / 'attempt.json'),
                          'collection_sha256': digest(root / (mode + '-collection') / 'collection.json'),
                          'handoff_sha256': digest(root / (mode + '-handoff.json'))}}
            seal_capture_json(root, mode + '-observations.json', report)
            # Only newly created preparation/input roots. Verification below uses retained custody.
            shutil.rmtree(task)
            shutil.rmtree(prepared)
            seal_capture_json(root, mode + '-capture-checks.json', verify_captures(root, report))
            reports.append(report)
        finally:
            for descriptor in descriptors:
                os.close(descriptor)
            socket_path.unlink(missing_ok=True)
            cleanup_group(child)
    seal_capture_json(root, 'observations.json', {
        'schema': 'caplab.cgroup-resource-probe-observations/v6', 'unit': unit,
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
        require(mount_coverage(coverage['raw'], usable_devices='writable_devices' in coverage) == coverage,
                'recorded mount coverage differs')
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
        for report in observation['reports']:
            require(verify_captures(root, report) == json.loads((root / (report['mode'] + '-capture-checks.json')).read_bytes()),
                    'capture checks differ after service exit')
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
    seal_capture_json(root, 'verification.json', {'schema': 'caplab.cgroup-resource-probe-verification/v6',
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
