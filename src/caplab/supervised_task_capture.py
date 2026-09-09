"""Task custody around a caller-owned blocked workload and retained directory."""

from dataclasses import asdict
from datetime import UTC, datetime
import os
from pathlib import Path, PurePosixPath
import stat
from typing import Mapping, Sequence

from caplab.process_capture import seal_capture_json
from caplab.task_capture import TaskCaptureError, TaskCaptureLimits, _Inventory, _changes
from caplab.task_capture_verify import _Reader, _open, _process


class SupervisedTaskCapture:
    """Single-owner recorder; caller owns launch, handoff, quiescence and cleanup.

    Enter before launching capture_process into output_dir/process. Capture the
    before tree while work is blocked, then release it. Finish after writers stop,
    with an independently retained process receipt digest. No process is launched
    or stopped here. Errors preserve custody and prohibit reuse of the recorder.
    """

    def __init__(self, command: Sequence[str], *, task_root: Path, namespace_root: str,
                 environment: Mapping[str, str], output_dir: Path,
                 limits: TaskCaptureLimits, max_process_receipt_bytes: int):
        if isinstance(command, (str, bytes)) or not command:
            raise ValueError('command must be a nonempty argument sequence')
        command = tuple(command)
        if not command or not command[0] or any(not isinstance(a, str) or '\0' in a for a in command):
            raise ValueError('invalid command arguments')
        if not isinstance(environment, Mapping):
            raise ValueError('environment must be an explicit string mapping')
        environment = dict(environment)
        if any(not isinstance(k, str) or not isinstance(v, str) or not k or '=' in k
               or '\0' in k or '\0' in v for k, v in environment.items()):
            raise ValueError('invalid environment')
        if (not isinstance(namespace_root, str) or not namespace_root.startswith('/')
                or namespace_root in ('/', '') or '\0' in namespace_root
                or namespace_root.startswith('//') or '..' in PurePosixPath(namespace_root).parts
                or str(PurePosixPath(namespace_root)) != namespace_root):
            raise ValueError('namespace root must be a canonical absolute path below root')
        if not isinstance(limits, TaskCaptureLimits):
            raise ValueError('invalid task capture limits')
        if type(max_process_receipt_bytes) is not int or max_process_receipt_bytes <= 0:
            raise ValueError('process receipt allowance must be a positive integer')
        task_root, output_dir = Path(task_root), Path(output_dir)
        if (not task_root.is_absolute() or task_root == Path('/') or task_root.resolve() != task_root
                or not task_root.is_dir()):
            raise ValueError('task root must be a resolved host directory below root')
        if (not output_dir.is_absolute() or output_dir.parent.resolve() != output_dir.parent
                or output_dir.is_relative_to(task_root) or task_root.is_relative_to(output_dir)):
            raise ValueError('output must have a resolved parent disjoint from the declared task')
        self.output_dir, self._limits = output_dir, limits
        self._receipt_limit = max_process_receipt_bytes
        self._intent = {'schema': 'caplab.task-capture-intent/v2', 'command': list(command),
            'cwd': str(task_root), 'environment': environment, 'limits': asdict(limits),
            'max_process_receipt_bytes': max_process_receipt_bytes,
            'task_source': {'kind': 'directory-descriptor', 'namespace_root': namespace_root}}
        self._state, self._fd = 'new', None

    def __enter__(self):
        if self._state != 'new':
            raise TaskCaptureError('supervised-capture-cannot-be-reentered')
        self._state = 'entering'
        self.output_dir.mkdir(mode=0o700)
        self.output_dir.chmod(0o700)
        self._intent_hash = seal_capture_json(self.output_dir, 'intent.json', self._intent)
        self._state = 'awaiting-before'
        return self

    def __exit__(self, error_type, error, traceback):
        finished = self._state == 'finished'
        self._state = 'closed'
        if self._fd is not None:
            os.close(self._fd)
            self._fd = None
        if error_type is None and not finished:
            raise TaskCaptureError('supervised-capture-exited-without-finish')

    def _snapshot(self, phase, bytes_left, entries_left):
        output = self.output_dir / phase
        output.mkdir(mode=0o700)
        started = datetime.now(UTC).isoformat()
        inventory = _Inventory(output, bytes_left, entries_left)
        inventory.visit(self._fd, '.', '.')
        root = inventory.entries[0]['source_stat']
        if (root['dev'], root['ino']) != (self._identity['device'], self._identity['inode']):
            raise TaskCaptureError('supervised-task-root-identity-differs')
        receipt = {'schema': 'caplab.task-inventory/v2',
            'source_root': self._intent['task_source']['namespace_root'],
            'descriptor_identity': dict(self._identity),
            'started_at': started, 'finished_at': datetime.now(UTC).isoformat(),
            'retained_bytes': inventory.retained_bytes,
            'entries': sorted(inventory.entries, key=lambda e: e['path'])}
        return receipt, seal_capture_json(output, 'inventory.json', receipt)

    def capture_before(self, descriptor: int, *, expected_device: int, expected_inode: int) -> str:
        """Seal the blocked task's before tree; return its byte digest for the supervisor."""
        if self._state != 'awaiting-before':
            self._state = 'failed'
            raise TaskCaptureError('supervised-before-out-of-order')
        self._state = 'capturing-before'
        if (any(type(v) is not int or v < 0 for v in (descriptor, expected_device, expected_inode))
                or expected_inode == 0):
            raise TaskCaptureError('invalid-supervised-task-descriptor')
        self._fd = os.dup(descriptor)
        info = os.fstat(self._fd)
        if not stat.S_ISDIR(info.st_mode) or (info.st_dev, info.st_ino) != (expected_device, expected_inode):
            raise TaskCaptureError('supervised-task-descriptor-identity-differs')
        for ancestor in (self.output_dir, *self.output_dir.parents):
            identity = ancestor.stat()
            if (identity.st_dev, identity.st_ino) == (expected_device, expected_inode):
                raise TaskCaptureError('supervised-output-overlaps-task-descriptor')
        self._identity = {'device': expected_device, 'inode': expected_inode}
        self._before, self._before_hash = self._snapshot('before', self._limits.max_task_bytes,
                                                       self._limits.max_task_entries)
        if len(self._before['entries']) == self._limits.max_task_entries:
            raise TaskCaptureError('task-entry-limit:no-final-root-allowance')
        self._state = 'before-captured'
        return self._before_hash

    def finish(self, *, expected_process_sha256: str) -> dict:
        """Verify the anchored process capture and retain the quiescent after tree."""
        if self._state != 'before-captured':
            self._state = 'failed'
            raise TaskCaptureError('supervised-finish-out-of-order')
        self._state = 'finishing'
        with _open(None, self.output_dir / 'process', directory=True) as process_root:
            process = _Reader(self._receipt_limit).receipt(process_root, 'capture.json', expected_process_sha256,
                                                           'caplab.process-capture/v1')
            _process(process_root, process, self._limits)
        after, after_hash = self._snapshot('after', self._limits.max_task_bytes - self._before['retained_bytes'],
                                           self._limits.max_task_entries - len(self._before['entries']))
        receipt = {'schema': 'caplab.task-attempt-capture/v2', 'intent_sha256': self._intent_hash,
            'before_inventory_sha256': self._before_hash, 'after_inventory_sha256': after_hash,
            'process_capture_sha256': expected_process_sha256,
            'retained_task_bytes': self._before['retained_bytes'] + after['retained_bytes'],
            'retained_task_entries': len(self._before['entries']) + len(after['entries']),
            'process': process, 'changes': _changes(self._before, after),
            'capture_complete': process['streams_complete'],
            'interpretation': 'observed task changes through a retained descriptor; caller owns workload blocking, '
                'quiescence and handoff provenance; no native execution binding or eligibility'}
        seal_capture_json(self.output_dir, 'attempt.json', receipt)
        self._state = 'finished'
        return receipt
