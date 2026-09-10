#!/usr/bin/env python3
"""Two fixed offline native startup probes; requires a new scoped authorization.

No model-serving surface, command override, credential or host home is exposed.
This is a diagnostic, not a native study launcher or completeness gate.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import stat
import subprocess
import time
import uuid

from caplab.capture_accounting import build_capture_byte_report
from caplab.capture_overlap import compare_verified_capture_overlap
from caplab.prepared_task_capture import verify_prepared_before
from caplab.exec_provenance import observe_exec_tracer, verify_exec_tracer
from caplab.exec_trace import inspect_exec_trace
from caplab.exec_trace_buffer import ExecTraceBuffer
from caplab.native_capture_invocation import NativeCaptureContext, build_native_capture_invocation
from caplab.native_collection import COLLECTION_SCHEMAS, NativeRuntimeDescriptor, collect_native_outputs
from caplab.native_collection_verify import verify_native_collection
from caplab.native_launch_configuration import (
    NativeLaunchContext, NativeLaunchTraceEvidence, build_native_launch_configuration, inspect_native_launch_trace,
)
from caplab.native_runtime import _validated_invocation, prepare_native_runtime
from caplab.preference.native_live import _launcher_environment
from caplab.process_capture import capture_process, seal_capture_json
from caplab.supervised_task_capture import SupervisedTaskCapture
from caplab.task_capture import TASK_ATTEMPT_SCHEMAS, TASK_INVENTORY_SCHEMAS, TaskCaptureLimits
from caplab.task_capture_verify import _Reader, _identity, _inventory, _open, _read_file, verify_task_capture
from probe_cgroup_resource_limits import (
    JOIN, MIB, MOUNTS, cleanup_group, digest, mount_coverage,
    populated, receive_mount, require, retain_mount, snapshot,
    verify_basic_devices, verify_nested_procfs,
)

SCRIPT = Path(__file__).resolve()
POLICY = SCRIPT.parent.parent / 'docs/product/contracts/native-agent-systems.json'
SOURCES = {'codex': Path('/home/halbritt/.npm-global/lib/node_modules/@openai/codex'),
           'claude': Path('/home/halbritt/.local/share/claude/versions/2.1.265')}
PROMPT = b'Startup diagnostic only. Reply with the single word READY. Do not change files or use tools.'
HANDOFF = """import array,json,os,resource,socket,sys
from pathlib import Path
plan=json.loads(sys.argv[1])
for relative in json.loads(sys.argv[2]):
    Path('/episode', *Path(relative).parts[1:]).mkdir(mode=0o700,exist_ok=True)
resource.setrlimit(resource.RLIMIT_CORE,(0,0))
if len(sys.argv)==6:
    if sys.argv[5]!='trace-exec':raise RuntimeError('unsupported handoff mode')
    resource.setrlimit(resource.RLIMIT_FSIZE,(67108864,67108864))
with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as channel:
    channel.settimeout(5)
    channel.connect('/control.sock')
    roots=[]
    try:
        for path in json.loads(sys.argv[3]):
            roots.append(os.open(path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW))
        channel.sendmsg([b'R'],[(socket.SOL_SOCKET,socket.SCM_RIGHTS,array.array('i',roots))])
    finally:
        for fd in roots:os.close(fd)
    if channel.recv(1)!=b'1':raise RuntimeError('supervisor refused startup')
command=json.loads(sys.argv[4])+plan['command']
os.execvpe(command[0],command,plan['environment'])
"""


def harness_manifest(root):
    """Hash the declared installation only; system runtime is outside this identity."""
    require(root.is_absolute() and root.resolve() == root, 'harness root must be resolved')
    entries, remaining = [], 1024 * MIB
    def visit(path, relative):
        nonlocal remaining
        require(len(entries) < 10000, 'harness manifest entry allowance exceeded')
        before = path.lstat()
        entry = {'path': relative, 'mode': stat.S_IMODE(before.st_mode)}
        entries.append(entry)
        if stat.S_ISDIR(before.st_mode):
            entry['kind'] = 'directory'
            with os.scandir(path) as children:
                for child in children:
                    visit(Path(child.path), child.name if relative == '.' else relative + '/' + child.name)
        elif stat.S_ISREG(before.st_mode):
            _, size, sha = _read_file(None, path, remaining, retain=False)
            entry.update(kind='file', bytes=size, sha256=sha)
            remaining -= size
        elif stat.S_ISLNK(before.st_mode):
            require(path.resolve().is_relative_to(root), 'harness symlink escapes installation')
            target = os.readlink(path)
            remaining -= len(os.fsencode(target))
            require(remaining >= 0, 'harness byte allowance exceeded')
            entry.update(kind='symlink', target=target)
        else:
            raise RuntimeError('unsupported harness source type')
        require(_identity(path.lstat()) == _identity(before), 'harness changed during inventory')
    visit(root, '.')
    return {'source': str(root), 'max_bytes': 1024 * MIB, 'max_entries': 10000,
            'bytes': 1024 * MIB - remaining, 'entries': sorted(entries, key=lambda e: e['path'])}


def inspect_network(peer_pid):
    parent = os.readlink('/proc/self/ns/net')
    peer = os.readlink(f'/proc/{peer_pid}/ns/net')
    network_raw = Path(f'/proc/{peer_pid}/net/dev').read_text()
    names = [line.split(':', 1)[0].strip() for line in network_raw.splitlines()[2:]]
    require(parent != peer and names == ['lo'], 'native peer lacks isolated loopback-only network')
    require(not any(Path(f'/proc/{peer_pid}/root/work').iterdir()), 'native startup task is not empty')
    return {'supervisor_network_namespace': parent, 'peer_network_namespace': peer,
            'interfaces_raw': network_raw, 'interfaces': names}


def stop_writers(child):
    forced = populated(child)
    if forced:
        (child / 'cgroup.kill').write_text('1')
        deadline = time.monotonic() + 3
        while populated(child) and time.monotonic() < deadline:
            time.sleep(.02)
    require(not populated(child), 'native child cgroup did not become quiescent')
    return forced


def inspect_traced_peer(peer_pid, trace_path):
    checks = inspect_network(peer_pid)
    namespaces = {name: {'supervisor': os.readlink('/proc/self/ns/' + name),
                        'peer': os.readlink(f'/proc/{peer_pid}/ns/{name}')} for name in ('mnt', 'pid')}
    require(all(item['supervisor'] != item['peer'] for item in namespaces.values()), 'tracer shares peer namespace')
    if not isinstance(trace_path, ExecTraceBuffer):
        require(not Path(f'/proc/{peer_pid}/root', str(trace_path).lstrip('/')).exists(), 'host trace path is exposed')
    tracer = observe_exec_tracer(peer_pid, trace_path, expected_tracer_executable=Path('/usr/bin/strace'))
    return checks | {'tracer_namespaces': namespaces, 'host_trace_path_exposed': False, 'exec_tracer': tracer}


def inspect_custody(root, report, *, expected_selections_sha256=None, expected_task_input=None,
                    expected_routing=None):
    name, anchors = report['harness'], report['anchors']
    task = verify_task_capture(root / name, expected_attempt_sha256=anchors['attempt_sha256'], max_receipt_bytes=300000)
    native = verify_native_collection(POLICY, root / (name + '-collection'),
        expected_collection_sha256=anchors['collection_sha256'], max_receipt_bytes=300000)
    accounting = build_capture_byte_report(POLICY, task_custody=root / name,
        collection_custody=root / (name + '-collection'), expected_attempt_sha256=anchors['attempt_sha256'],
        expected_collection_sha256=anchors['collection_sha256'], max_receipt_bytes=300000)
    require(digest(root / (name + '-handoff.json')) == anchors['handoff_sha256'], 'handoff hash differs')
    handoff = json.loads((root / (name + '-handoff.json')).read_bytes())
    require(handoff == report['handoff'], 'handoff observation differs')
    coverage = handoff['mount_coverage']
    nested_userns = 'writable_procfs' in coverage
    devices = coverage.get('device_profile', 'writable_devices' in coverage)
    require(mount_coverage(coverage['raw'], usable_devices=devices,
                          nested_userns=nested_userns) == coverage, 'mount coverage differs')
    if devices == 'bwrap-basic-v1':
        verify_basic_devices(handoff.get('device_access'))
    if nested_userns:
        verify_nested_procfs(handoff.get('nested_procfs'))
    network = handoff['peer_checks']
    require(network['supervisor_network_namespace'] != network['peer_network_namespace']
            and network['interfaces'] == ['lo'], 'recorded network isolation differs')
    routing = None
    if expected_routing is None:
        require('routing' not in network, 'routed capture requires independent routing anchors')
    else:
        from caplab.capture_network_verify import verify_capture_routing
        require(isinstance(expected_routing, dict) and set(expected_routing) ==
                {'plan', 'terminal_sha256'} | ({'namespace_profile'} if 'namespace_profile' in expected_routing else set()),
                'invalid expected routing evidence')
        require('namespace_profile' not in expected_routing or expected_routing['namespace_profile'] == 'parent-user/v1',
                'invalid selected routing namespace profile')
        ready = network.get('routing')
        require(isinstance(ready, dict), 'routed handoff lacks readiness')
        ready_sha = hashlib.sha256((json.dumps(ready, sort_keys=True) + '\n').encode()).hexdigest()
        routing = verify_capture_routing(root / (name + '-network'),
            plan=expected_routing['plan'],
            expected_policy_sha256=expected_routing['plan']['network_policy_sha256'],
            expected_terminal_sha256=expected_routing['terminal_sha256'],
            expected_ready_sha256=ready_sha, expected_peer_pid=handoff['peer_pid'],
            expected_namespace_profile=expected_routing.get('namespace_profile', 'workload-user/v1'))
    before_reader = _Reader(300000)
    with _open(None, root / name, directory=True) as fd:
        attempt = before_reader.receipt(fd, 'attempt.json', anchors['attempt_sha256'], TASK_ATTEMPT_SCHEMAS)
        require(attempt['before_inventory_sha256'] == handoff['before_inventory_sha256'],
                'pre-release task anchor differs')
        with _open(fd, 'before', directory=True) as before_fd:
            before = before_reader.receipt(before_fd, 'inventory.json', attempt['before_inventory_sha256'],
                                           TASK_INVENTORY_SCHEMAS)
    prepared_task = None
    if expected_task_input is None:
        require('prepared_task' not in handoff, 'unexpected prepared task handoff')
        require([e['path'] for e in before['entries']] == ['.'], 'startup task was not empty before release')
    else:
        prepared_task = verify_prepared_before(expected_task_input, before, handoff.get('prepared_task'),
                                               expected_before_sha256=attempt['before_inventory_sha256'])
    require(task['return_code'] == report['process']['return_code'] and
            task['termination'] == report['process']['termination'], 'resource and task outcomes differ')
    for source, path in ((task['task_source'], '/work'), (native['runtime_source'], '/episode')):
        identity = handoff['mounts'][MOUNTS.index(path)]
        require((source['namespace_root'], source['device'], source['inode']) ==
                (path, identity['source_dev'], identity['source_ino']), 'capture source differs from handoff')
    bytes_left, entries_left = 40 * MIB, 2000
    retained_receipts = {}
    require([i['source_root'] for i in report['inventories']] == list(MOUNTS), 'incomplete mount custody')
    for index, item in enumerate(report['inventories']):
        identity = handoff['mounts'][index]
        with _open(None, root / (name + '-retained') / str(index), directory=True) as fd:
            receipt = _Reader(1000000).receipt(fd, 'inventory.json', item['inventory_sha256'],
                                               'caplab.retained-mount-inventory/v1')
            require(receipt['descriptor_identity'] == identity and
                    (receipt['max_retained_bytes'], receipt['max_entries']) == (bytes_left, entries_left),
                    'retained mount identity or combined allowance differs')
            size, count = _inventory(fd, receipt, cwd=MOUNTS[index], bytes_left=bytes_left, entries_left=entries_left)
            bytes_left -= size; entries_left -= count
            retained_receipts[MOUNTS[index]] = receipt
    require(report['retained_bytes'] == 40 * MIB - bytes_left and
            report['retained_entries'] == 2000 - entries_left, 'retained totals differ')
    reader = _Reader(300000)
    with _open(None, root / name, directory=True) as fd:
        attempt = reader.receipt(fd, 'attempt.json', anchors['attempt_sha256'], TASK_ATTEMPT_SCHEMAS)
        with _open(fd, 'after', directory=True) as after_fd:
            after = reader.receipt(after_fd, 'inventory.json', attempt['after_inventory_sha256'],
                                   TASK_INVENTORY_SCHEMAS)
    with _open(None, root / (name + '-collection'), directory=True) as fd:
        collection = _Reader(300000).receipt(fd, 'collection.json', anchors['collection_sha256'],
                                            COLLECTION_SCHEMAS)
    overlap = compare_verified_capture_overlap(task_after=after, native=collection,
        retained_task=retained_receipts['/work'], retained_runtime=retained_receipts['/episode'])
    execution = inspect_execution(root, report, native, expected_selections_sha256=expected_selections_sha256)
    return {'task': task, 'native': native, 'accounting': accounting, 'overlap': overlap, **execution,
            **({'routing': routing} if routing is not None else {}),
            **({'prepared_task': prepared_task} if prepared_task is not None else {}),
            'native_launch_attempted_by_supervisor': True, 'model_execution_verified': False,
            'native_capture_complete': None, 'study_eligible': False}


def inspect_execution(root, report, native, *, expected_selections_sha256=None):
    if expected_selections_sha256 is None and 'exec_trace_sha256' not in report['anchors']:
        return {}
    if expected_selections_sha256 is not None:
        require(isinstance(expected_selections_sha256, str) and
                re.fullmatch(r'[0-9a-f]{64}', expected_selections_sha256) is not None,
                'invalid startup selection anchor')
    name = report['harness']
    anchors, handoff = report['anchors'], report['handoff']
    network = handoff['peer_checks']
    execution = {}
    selections = json.loads((root / 'selections.json').read_bytes())
    selected, = [item for item in selections if item['harness'] == name]
    plan = _validated_invocation(POLICY, selected['plan'], native['invocation_sha256'])
    selection_hash = digest(root / 'selections.json')
    require(selection_hash == json.loads((root / 'intent.json').read_bytes())['selections_sha256'],
            'traced selections differ from sealed intent')
    require(expected_selections_sha256 is None or selection_hash == expected_selections_sha256,
            'startup selection anchor differs')
    termination_required = selected.get('entrypoint_termination_required', False)
    require(type(termination_required) is bool, 'invalid termination requirement')
    require(not termination_required or 'launch_configuration' in selected,
            'required termination needs a launch configuration')
    require(not termination_required or 'exec_trace_sha256' in anchors,
            'required termination needs an exec trace')
    if 'exec_trace_sha256' in anchors:
        require(network['host_trace_path_exposed'] is False and all(
            item['supervisor'] != item['peer'] for item in network['tracer_namespaces'].values()),
            'recorded tracer custody isolation differs')
        if 'launch_configuration' in selected:
            launch = selected['launch_configuration']
            execution['launch_configuration'] = inspect_native_launch_trace(POLICY, plan, launch,
                root / (name + '-exec.trace'), evidence=NativeLaunchTraceEvidence(native['invocation_sha256'],
                    launch['launch_configuration_sha256'], anchors['exec_trace_sha256'], handoff['peer_pid'], MIB),
                require_termination=termination_required)
            execution['exec_trace'] = execution['launch_configuration']['exec_trace']
        else:
            execution['exec_trace'] = inspect_exec_trace(root / (name + '-exec.trace'),
                expected_trace_sha256=anchors['exec_trace_sha256'], expected_pid=handoff['peer_pid'],
                expected_executable='/toolbin/' + name, expected_command=plan['command'],
                expected_environment=plan['environment'], max_trace_bytes=MIB)
        if 'exec_tracer' in network:
            execution['exec_tracer'] = verify_exec_tracer(network['exec_tracer'], root / (name + '-exec.trace'),
                                                        expected_pid=handoff['peer_pid'])
    return execution


def inside(root, unit, *, trace_claude=False, trace_exec=False):
    require(not (trace_claude and trace_exec), 'trace modes are mutually exclusive')
    require(re.fullmatch(r'caplab-native-startup-[0-9a-f]{32}\.service', unit), 'invalid native startup unit')
    membership = Path('/proc/self/cgroup').read_text().strip()
    require(membership.startswith('0::/') and '\n' not in membership, 'unified cgroup required')
    current = Path('/sys/fs/cgroup') / membership[3:].lstrip('/')
    require(current.name == 'supervisor' and current.parent.name == unit, 'wrong supervisor cgroup')
    group = current.parent
    for name, value in {'memory.max': str(512 * MIB), 'memory.swap.max': '0', 'pids.max': '128'}.items():
        require((group / name).read_text().strip() == value, 'outer resource limit differs')
    (group / 'cgroup.subtree_control').write_text('+memory +pids')
    selections = json.loads((root / 'selections.json').read_bytes())
    selection_anchor = None
    if trace_exec:
        selection_anchor = json.loads((root / 'intent.json').read_bytes())['selections_sha256']
        require(digest(root / 'selections.json') == selection_anchor,
                'traced selections differ before launch')
    require([s['harness'] for s in selections] == (['claude'] if trace_claude else list(SOURCES)),
            'startup selection differs from fixed diagnostic mode')
    reports = []
    for selected in selections:
        name = selected['harness']; source = SOURCES[name]; plan = selected['plan']
        if trace_exec:
            require(selected.get('entrypoint_termination_required') is True,
                    'new traced startup requires entrypoint termination')
            expected_launch = build_native_launch_configuration(POLICY, plan,
                expected_invocation_sha256=plan['invocation_sha256'], context=NativeLaunchContext('canonical-native/v1'))
            require(json.dumps(selected['launch_configuration'], sort_keys=True, allow_nan=False) ==
                    json.dumps(expected_launch, sort_keys=True, allow_nan=False), 'startup launch configuration differs')
        trace_prefix = ['/usr/bin/strace', '-f', '-s', '256', '-e', 'trace=%file,%process,%signal',
                        '-o', '/scratch/trace.log', '--'] if trace_claude else []
        if trace_claude or trace_exec:
            require(digest(Path('/usr/bin/strace')) == selected['strace_sha256'], 'strace differs before launch')
        require(harness_manifest(source) == selected['harness_manifest'], 'harness differs before launch')
        task, prepared = root / (name + '-task'), root / (name + '-prepared')
        preparation = json.loads((prepared / 'preparation.json').read_bytes())
        require(digest(prepared / 'preparation.json') == selected['preparation_sha256'], 'preparation anchor differs')
        child = group / ('fixture-' + name); child.mkdir()
        descriptors = []; socket_path = root / (name + '-control.sock')
        try:
            limits = {'memory.max': str(256 * MIB), 'memory.swap.max': '0', 'memory.oom.group': '1', 'pids.max': '64'}
            for key, value in limits.items(): (child / key).write_text(value)
            before = snapshot(child)
            require(all(before['limits_and_usage'][key] == value for key, value in limits.items()), 'child limits differ')
            require(not populated(child), 'child populated before launch')
            executable = '/opt/native/bin/codex.js' if name == 'codex' else '/opt/native'
            command = ['/usr/bin/python3', '-B', '-c', JOIN, str(child), '/usr/bin/bwrap',
                '--unshare-all', '--die-with-parent', '--new-session', '--clearenv',
                '--ro-bind', '/usr', '/usr', '--symlink', 'usr/bin', '/bin', '--symlink', 'usr/lib', '/lib',
                '--symlink', 'usr/lib64', '/lib64', '--proc', '/proc', '--dir', '/dev',
                '--dev-bind', '/dev/null', '/dev/null', '--dev-bind', '/dev/urandom', '/dev/urandom',
                '--dir', '/opt', '--ro-bind', str(source), '/opt/native', '--dir', '/toolbin',
                '--symlink', executable, '/toolbin/' + name]
            for mount in MOUNTS: command += ['--size', str(64 * MIB), '--tmpfs', mount]
            command += ['--ro-bind', str(socket_path), '/control.sock', '--chdir', '/work',
                '--remount-ro', '/proc', '--remount-ro', '/', '--', '/usr/bin/python3', '-B', '-c', HANDOFF,
                json.dumps(plan), json.dumps(preparation['directories']), json.dumps(MOUNTS), json.dumps(trace_prefix)]
            if trace_exec:
                command.append('trace-exec')
                command = ['/usr/bin/prlimit', '--fsize=1048576:67108864', '--core=0', '--',
                    '/usr/bin/strace', '-f', '-v', '-xx', '-s', '65536', '-e', 'trace=execve,execveat',
                    '-o', str(root / (name + '-exec.trace')), '--', *command]
            seal_capture_json(root, name + '-launch.json', {'command': command, 'before': before, 'plan': plan})
            with SupervisedTaskCapture(command, task_root=task, namespace_root='/work', environment=_launcher_environment(),
                    output_dir=root / name, limits=TaskCaptureLimits(200000, MIB, 1000, 20), max_process_receipt_bytes=30000) as recorder:
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as listener:
                    listener.bind(str(socket_path)); socket_path.chmod(0o600); listener.listen(1); listener.settimeout(5)
                    with ThreadPoolExecutor(max_workers=1) as pool:
                        future = pool.submit(capture_process, command, cwd=task, environment=_launcher_environment(),
                            output_dir=root / name / 'process', max_stream_bytes=200000, timeout_seconds=20)
                        descriptors, handoff = receive_mount(listener, child, recorder,
                            inspect_peer=(lambda pid: inspect_traced_peer(pid, root / (name + '-exec.trace')))
                                if trace_exec else inspect_network, usable_devices=True)
                        process = future.result(timeout=26)
                forced = stop_writers(child)
                after = snapshot(child)
                seal_capture_json(root, name + '-resource-exit.json',
                    {'before': before, 'after': after, 'process': process, 'forced_group_kill': forced})
                recorder.finish(expected_process_sha256=digest(root / name / 'process/capture.json'))
                index = MOUNTS.index('/episode'); identity = handoff['mounts'][index]
                collect_native_outputs(POLICY, prepared, expected_preparation_sha256=selected['preparation_sha256'],
                    output_dir=root / (name + '-collection'), max_receipt_bytes=100000,
                    max_artifact_bytes=8 * MIB, max_entries=1000,
                    runtime_descriptor=NativeRuntimeDescriptor(descriptors[index], identity['source_dev'], identity['source_ino']))
            retained = root / (name + '-retained'); retained.mkdir(mode=0o700)
            inventories, bytes_left, entries_left = [], 40 * MIB, 2000
            for index, (descriptor, identity) in enumerate(zip(descriptors, handoff['mounts'], strict=True)):
                sha, bytes_left, entries_left = retain_mount(descriptor, retained / str(index), identity, bytes_left, entries_left)
                inventories.append({'source_root': identity['source_root'], 'inventory_sha256': sha})
            report = {'harness': name, 'before': before, 'after': after, 'process': process, 'handoff': handoff,
                'forced_group_kill': forced, 'inventories': inventories, 'retained_bytes': 40 * MIB - bytes_left,
                'retained_entries': 2000 - entries_left, 'anchors': {'attempt_sha256': digest(root / name / 'attempt.json'),
                    'collection_sha256': digest(root / (name + '-collection') / 'collection.json'),
                    'handoff_sha256': digest(root / (name + '-handoff.json'))}}
            if trace_exec:
                require((root / (name + '-exec.trace')).stat().st_size < MIB, 'execution trace reached file limit')
                report['anchors']['exec_trace_sha256'] = digest(root / (name + '-exec.trace'))
            seal_capture_json(root, name + '-observations.json', report)
            require(harness_manifest(source) == selected['harness_manifest'], 'harness changed during startup')
            if trace_claude or trace_exec:
                require(digest(Path('/usr/bin/strace')) == selected['strace_sha256'], 'strace changed during startup')
            seal_capture_json(root, name + '-checks.json', inspect_custody(root, report,
                expected_selections_sha256=selection_anchor))
            reports.append(report)
        finally:
            for fd in descriptors: os.close(fd)
            socket_path.unlink(missing_ok=True)
            cleanup_group(child)
    seal_capture_json(root, 'observations.json', {'unit': unit, 'delegated_cgroup': str(group), 'reports': reports})


def run(root, *, trace_claude=False, trace_exec=False):
    require(not (trace_claude and trace_exec), 'trace modes are mutually exclusive')
    require(root.is_absolute() and root.parent.resolve() == root.parent and not root.exists(), 'output must be fresh and resolved')
    root.mkdir(mode=0o700)
    selections = []
    for name, source in SOURCES.items():
        if trace_claude and name != 'claude':
            continue
        manifest = harness_manifest(source)
        task = root / (name + '-task'); task.mkdir(mode=0o700)
        plan = build_native_capture_invocation(POLICY, 'codex-terra-max' if name == 'codex' else 'claude-fable-5-max',
            context=NativeCaptureContext('/work', '/episode', PROMPT, None if name == 'codex' else str(uuid.uuid4())))
        prepared = root / (name + '-prepared')
        prepare_native_runtime(POLICY, plan, expected_invocation_sha256=plan['invocation_sha256'], task_root=task, output_dir=prepared)
        selections.append({'harness': name, 'harness_manifest': manifest, 'plan': plan,
                           'preparation_sha256': digest(prepared / 'preparation.json'),
                           **({'entrypoint_termination_required': True,
                               'launch_configuration': build_native_launch_configuration(POLICY, plan,
                               expected_invocation_sha256=plan['invocation_sha256'],
                               context=NativeLaunchContext('canonical-native/v1'))} if trace_exec else {}),
                           **({'strace_sha256': digest(Path('/usr/bin/strace'))} if trace_claude or trace_exec else {})})
    selection_hash = seal_capture_json(root, 'selections.json', selections)
    unit = 'caplab-native-startup-' + uuid.uuid4().hex + '.service'
    environment = {**_launcher_environment(), 'XDG_RUNTIME_DIR': f'/run/user/{os.getuid()}',
                   'DBUS_SESSION_BUS_ADDRESS': f'unix:path=/run/user/{os.getuid()}/bus'}
    command = ['/usr/bin/systemd-run', '--user', '--unit=' + unit, '--wait', '--pipe', '--collect',
        '--service-type=exec', '--property=Delegate=memory pids', '--property=DelegateSubgroup=supervisor',
        '--property=MemoryMax=536870912', '--property=MemorySwapMax=0', '--property=TasksMax=128',
        '--property=RuntimeMaxSec=75', '--property=OOMPolicy=continue', '--property=KillMode=control-group',
        '--property=LimitCORE=0', '--', '/usr/bin/env', '-i', 'PATH=/usr/bin:/bin', 'LANG=C.UTF-8',
        'PYTHONPATH=' + str(SCRIPT.parent.parent / 'src'), '/usr/bin/python3', '-B', str(SCRIPT),
        '--output-root', str(root), '--inside-unit', unit]
    if trace_claude:
        command.append('--trace-claude')
    if trace_exec:
        command.append('--trace-exec')
    seal_capture_json(root, 'intent.json', {'unit': unit, 'command': command, 'environment': environment,
        'selections_sha256': selection_hash, 'script_sha256': digest(SCRIPT),
        'resource_probe_sha256': digest(SCRIPT.with_name('probe_cgroup_resource_limits.py'))})
    try:
        process = capture_process(command, cwd=root, environment=environment, output_dir=root / 'service',
                                  max_stream_bytes=200000, timeout_seconds=85)
        require(process['return_code'] == 0 and process['streams_complete'], 'startup supervisor failed; inspect retained output')
        observation = json.loads((root / 'observations.json').read_bytes())
        require([r['harness'] for r in observation['reports']] == [s['harness'] for s in selections],
                'incomplete startup population')
        for report in observation['reports']:
            require(inspect_custody(root, report, expected_selections_sha256=selection_hash if trace_exec else None) ==
                    json.loads((root / (report['harness'] + '-checks.json')).read_bytes()),
                    'custody checks changed after namespace exit')
    finally:
        stopped = subprocess.run(['/usr/bin/systemctl', '--user', 'stop', unit], env=environment, capture_output=True, timeout=5)
        state = subprocess.run(['/usr/bin/systemctl', '--user', 'show', unit, '--property=LoadState', '--value'],
                               env=environment, capture_output=True, timeout=5)
        seal_capture_json(root, 'cleanup.json', {'unit': unit, 'stop_return_code': stopped.returncode,
            'stop_stdout': stopped.stdout.decode(), 'stop_stderr': stopped.stderr.decode(),
            'show_return_code': state.returncode, 'load_state': state.stdout.decode().strip(), 'show_stderr': state.stderr.decode()})
        require(state.returncode == 0 and state.stdout.strip() == b'not-found', 'native startup unit remains')
    require(not Path(observation['delegated_cgroup']).exists(), 'native startup cgroup remains')
    seal_capture_json(root, 'verification.json', {'schema': 'caplab.offline-native-startup-verification/v1',
        'unit': unit, 'startup_capture_count': len(selections), 'trace_claude': trace_claude,
        'trace_exec': trace_exec, 'unit_removed': True,
        'remote_model_execution': False, 'native_capture_complete': None, 'study_eligible': False})
    print(json.dumps({'root': str(root), 'unit': unit, 'verified': True}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root', type=Path, required=True)
    parser.add_argument('--inside-unit', help=argparse.SUPPRESS)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--trace-claude', action='store_true', help='Single offline Claude syscall diagnostic; requires new authorization')
    modes.add_argument('--trace-exec', action='store_true', help='Supervisor-owned offline exec traces; requires new authorization')
    args = parser.parse_args()
    if args.inside_unit:
        inside(args.output_root, args.inside_unit, trace_claude=args.trace_claude, trace_exec=args.trace_exec)
    else:
        run(args.output_root, trace_claude=args.trace_claude, trace_exec=args.trace_exec)
