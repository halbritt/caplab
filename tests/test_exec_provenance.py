"""A real paused peer identifies the outside tracer before executing a witness."""
from contextlib import contextmanager, ExitStack
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import socket
import struct
import subprocess
import sys
import tempfile
import unittest

from caplab.exec_provenance import observe_exec_tracer, verify_exec_tracer
from caplab.exec_trace import inspect_exec_trace
from caplab.exec_trace_buffer import buffered_exec_trace
from caplab.revbench.codex import ExactSecretStreamQuarantine
from caplab.task_capture_verify import CaptureVerificationError

ENV = {'LANG': 'C.UTF-8', 'PATH': '/usr/bin:/bin'}
COMMAND = ['/usr/bin/env', '--', '/usr/bin/python3', '-B', '-c', "print('CAPLAB café provenance')"]
GUARD = r'''import json,os,socket,sys
with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as channel:
 channel.connect('/control.sock')
 channel.sendall(b'R')
 if channel.recv(1)!=b'1':sys.exit(7)
os.execve('/usr/bin/env',json.loads(sys.argv[1]),json.loads(sys.argv[2]))
'''

@unittest.skipUnless(all(Path(p).is_file() for p in ('/usr/bin/bwrap','/usr/bin/strace')), 'Bubblewrap and strace required')
class ExecProvenanceTests(unittest.TestCase):
    @contextmanager
    def paused_peer(self, *, expected_exit=0, traced=True, expose_trace=False, isolated=True, buffered=False):
        before=set(os.listdir('/proc/self/fd'))
        with tempfile.TemporaryDirectory() as temporary, ExitStack() as stack:
            root=Path(temporary);trace=root/'exec.trace';sock=root/'control.sock'
            buffer = stack.enter_context(buffered_exec_trace(max_bytes=1048576,
                quarantine_factory=lambda: ExactSecretStreamQuarantine((b'fabricated-private-control',)))) if buffered else None
            command=['/usr/bin/bwrap','--unshare-all','--die-with-parent','--new-session','--clearenv',
                '--cap-drop','ALL','--ro-bind','/usr','/usr','--symlink','usr/bin','/bin',
                '--symlink','usr/lib','/lib','--symlink','usr/lib64','/lib64','--proc','/proc',
                '--dev','/dev','--tmpfs','/work','--ro-bind',str(sock),'/control.sock',
                '--chdir','/work','--remount-ro','/','--','/usr/bin/python3','-B','-c',GUARD,
                json.dumps(COMMAND),json.dumps(ENV)]
            if expose_trace:command[1:1]=['--ro-bind',str(root),str(root)]
            if not isolated:command.remove('--unshare-all')
            if traced:
                command=['/usr/bin/strace','-f','-v','-xx','-s','65536','-e','trace=execve,execveat','-o',str(buffer.path if buffer else trace),'--']+command
            command=['/usr/bin/timeout','--kill-after=1','10','/usr/bin/prlimit','--fsize=1048576:1048576','--core=0','--']+command
            with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as listener:
                listener.bind(str(sock));listener.listen(1);listener.settimeout(5)
                child=subprocess.Popen(command,env=ENV,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                try:
                    channel,_=listener.accept()
                    with channel:
                        channel.settimeout(3)
                        peer,uid,gid=struct.unpack('3i',channel.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
                        self.assertEqual((uid,gid),(os.getuid(),os.getgid()))
                        self.assertEqual(channel.recv(1),b'R')
                        yield root,buffer if buffer else trace,peer,channel
                    stdout,stderr=child.communicate(timeout=12)
                    self.assertEqual(child.returncode,expected_exit,stderr.decode())
                    if child.returncode==0:
                        retention = buffer.retain(trace) if buffer else None
                        self.assertEqual(stdout,'CAPLAB café provenance\n'.encode())
                        checked=inspect_exec_trace(trace,expected_trace_sha256=hashlib.sha256(trace.read_bytes()).hexdigest(),
                            expected_pid=peer,expected_executable='/usr/bin/env',expected_command=COMMAND,
                            expected_environment=ENV,max_trace_bytes=1048576)
                        self.assertTrue(checked['successful_execve_agrees'])
                        self.assertFalse(checked['binding_complete'])
                        observation=json.loads((root/'observation.json').read_bytes())
                        self.assertTrue(verify_exec_tracer(observation,trace,expected_pid=peer,
                            **({'trace_retention': retention} if buffer else {}))['recorded_tracer_custody_agrees'])
                        if buffer:
                            self.assertNotEqual(observation['trace_identity'], retention['retained_identity'])
                            for changed in (retention | {'trace_sha256': '0'*64},
                                            retention | {'source_identity': retention['retained_identity']},
                                            retention | {'quarantine_applied': False},
                                            retention | {'source_seals': 0}):
                                with self.subTest(changed=changed), self.assertRaises(ValueError):
                                    verify_exec_tracer(observation,trace,expected_pid=peer,trace_retention=changed)
                    else:
                        self.assertEqual(child.returncode,7,stderr.decode())
                        self.assertEqual(stdout,b'')
                finally:
                    if child.poll() is None:child.kill()
                    child.communicate(timeout=3)
        self.assertEqual(before,set(os.listdir('/proc/self/fd')))

    def test_anonymous_trace_identity_links_to_a_guarded_retained_copy(self):
        with self.paused_peer(buffered=True) as (root,buffer,peer,channel):
            observation=observe_exec_tracer(peer,buffer,expected_tracer_executable=Path('/usr/bin/strace'))
            self.assertEqual(observation['schema'], 'caplab.exec-tracer-observation/v2')
            self.assertEqual(observation['trace_storage'], 'sealed-buffer/v1')
            self.assertEqual(observation['trace_identity'], buffer.identity)
            self.assertFalse((root/'exec.trace').exists())
            (root/'observation.json').write_text(json.dumps(observation))
            channel.sendall(b'1')

    def test_authenticated_peer_executes_through_observed_outside_tracer(self):
        with self.paused_peer() as (root,trace,peer,channel):
            observation=observe_exec_tracer(peer,trace,expected_tracer_executable=Path('/usr/bin/strace'))
            self.assertEqual(observation['peer_pid'],peer)
            verified=verify_exec_tracer(observation,trace,expected_pid=peer)
            self.assertTrue(verified['recorded_tracer_custody_agrees'])
            (root/'observation.json').write_text(json.dumps(observation))
            channel.sendall(b'1')


    def test_malformed_observations_cannot_supply_custody_evidence(self):
        with self.paused_peer(expected_exit=7) as (root,trace,peer,channel):
            observation=observe_exec_tracer(peer,trace,expected_tracer_executable=Path('/usr/bin/strace'))
            candidates=[None,{},observation|{'peer_pid':True},observation|{'tracer_pid':False},
                        observation|{'trace_descriptor_flags':True},observation|{'supervisor_namespaces':{}},
                        observation|{'supervisor_cgroup':'','tracer_cgroup':''}]
            for value in candidates:
                with self.subTest(value=value),self.assertRaises(CaptureVerificationError):
                    verify_exec_tracer(value,trace,expected_pid=peer)

    def test_native_startup_handoff_records_the_actual_tracer(self):
        scripts=Path(__file__).resolve().parents[1]/'scripts'
        sys.path.insert(0,str(scripts))
        try:
            spec=importlib.util.spec_from_file_location('native_startup_provenance',scripts/'probe_native_capture_startup.py')
            startup=importlib.util.module_from_spec(spec);spec.loader.exec_module(startup)
        finally:
            sys.path.pop(0)
        with self.paused_peer() as (root,trace,peer,channel):
            checks=startup.inspect_traced_peer(peer,trace)
            observation=checks['exec_tracer']
            self.assertEqual(observation['peer_pid'],peer)
            self.assertEqual(checks['interfaces'],['lo'])
            (root/'observation.json').write_text(json.dumps(observation))
            channel.sendall(b'1')

    def test_wrong_tracer_executable_or_output_file_prevents_release(self):
        with self.paused_peer(expected_exit=7) as (root,trace,peer,channel):
            with self.assertRaisesRegex(CaptureVerificationError,'tracer executable differs'):
                observe_exec_tracer(peer,trace,expected_tracer_executable=Path('/usr/bin/python3'))
            other=root/'other.trace';other.write_bytes(trace.read_bytes())
            with self.assertRaisesRegex(CaptureVerificationError,'exact trace descriptor'):
                observe_exec_tracer(peer,other,expected_tracer_executable=Path('/usr/bin/strace'))

    def test_missing_tracer_prevents_release(self):
        with self.paused_peer(expected_exit=7,traced=False) as (root,trace,peer,channel):
            with self.assertRaisesRegex(CaptureVerificationError,'has no tracer'):
                observe_exec_tracer(peer,trace,expected_tracer_executable=Path('/usr/bin/strace'))

    def test_exposed_trace_prevents_release(self):
        with self.paused_peer(expected_exit=7,expose_trace=True) as (root,trace,peer,channel):
            with self.assertRaisesRegex(CaptureVerificationError,'trace path is exposed'):
                observe_exec_tracer(peer,trace,expected_tracer_executable=Path('/usr/bin/strace'))

    def test_shared_peer_namespace_prevents_release(self):
        with self.paused_peer(expected_exit=7,isolated=False) as (root,trace,peer,channel):
            with self.assertRaisesRegex(CaptureVerificationError,'shares supervisor namespace'):
                observe_exec_tracer(peer,trace,expected_tracer_executable=Path('/usr/bin/strace'))

    def test_retained_contradictions_and_replaced_trace_are_refused(self):
        with self.paused_peer(expected_exit=7) as (root,trace,peer,channel):
            observation=observe_exec_tracer(peer,trace,expected_tracer_executable=Path('/usr/bin/strace'))
            untouched=deepcopy(observation)
            candidates=[observation|{'peer_pid':peer+1},observation|{'host_trace_path_exposed':True},
                observation|{'tracer_cgroup':'0::/other\n'},observation|{'trace_descriptor_flags':os.O_RDONLY},
                observation|{'tracer_pid':peer}]
            for name in ('mnt','pid','user','net'):
                bad=deepcopy(observation);bad['peer_namespaces'][name]=bad['supervisor_namespaces'][name];candidates.append(bad)
                bad=deepcopy(observation);bad['tracer_namespaces'][name]=bad['peer_namespaces'][name];candidates.append(bad)
            for value in candidates:
                with self.subTest(value=value),self.assertRaises(CaptureVerificationError):
                    verify_exec_tracer(value,trace,expected_pid=peer)
            self.assertEqual(observation,untouched)
            raw=trace.read_bytes();trace.rename(root/'original.trace');trace.write_bytes(raw)
            with self.assertRaisesRegex(CaptureVerificationError,'trace identity differs'):
                verify_exec_tracer(observation,trace,expected_pid=peer)
            trace.unlink();trace.symlink_to(root/'original.trace')
            with self.assertRaisesRegex(CaptureVerificationError,'regular file'):
                verify_exec_tracer(observation,trace,expected_pid=peer)
