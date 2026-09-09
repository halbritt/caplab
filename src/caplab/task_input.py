"""Anchored task inputs and verified creation in an empty caller-owned directory."""

from contextlib import contextmanager
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat

from caplab.process_capture import seal_capture_json
from caplab.task_capture import _inventory as _capture_inventory, _names, _unchanged
from caplab.task_capture_verify import _Reader, _count, _digest, _inventory, _open, _read_file, _require


POLICY = 'caplab.task-input-materialization-policy/v1'


def _positive(value, label):
    _require(_count(value, label) > 0, label + ' must be positive')
    return value


def _policy(entries):
    for entry in entries:
        mode, kind = entry['mode'], entry['kind']
        _require(mode <= 0o777, 'task input privilege bits are unsupported')
        if kind == 'directory':
            _require(mode & 0o500 == 0o500, 'task input directory must allow owner read and search')
        elif kind == 'file':
            _require(mode & 0o400 != 0, 'task input file must allow owner read')
        else:
            _require(mode == 0o777, 'task input symlink mode is unsupported')


def _content_hash(entries):
    fields = ('path', 'kind', 'mode', 'bytes', 'sha256', 'target_base64')
    content = [{key: entry[key] for key in fields if key in entry} for entry in entries]
    return hashlib.sha256(json.dumps(content, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')).hexdigest()


def prepare_task_input(source_root: Path, *, output_dir: Path, max_task_bytes: int, max_task_entries: int) -> str:
    """Retain a quiescent input once; return the hash the caller must retain independently.

    Source and custody parents must be trusted and stable. Partial custody is
    preserved on failure. No task correctness, exposure or admission is decided.
    """
    _positive(max_task_bytes, 'task byte limit'); _positive(max_task_entries, 'task entry limit')
    source, output = Path(source_root), Path(output_dir)
    _require(source.is_absolute() and source != Path('/') and source.resolve() == source and source.is_dir(),
             'task input source must be a resolved directory below root')
    _require(output.is_absolute() and output.parent.resolve() == output.parent and
             not output.is_relative_to(source) and not source.is_relative_to(output), 'input custody overlaps source or has unresolved parents')
    output.mkdir(mode=0o700); output.chmod(0o700)
    inventory, inventory_hash = _capture_inventory(source, output / 'inventory', max_task_bytes, max_task_entries)
    _policy(inventory['entries'])
    receipt = {'schema': 'caplab.task-input/v1', 'source_root': str(source),
        'inventory_sha256': inventory_hash, 'max_task_bytes': max_task_bytes, 'max_task_entries': max_task_entries,
        'retained_task_bytes': inventory['retained_bytes'], 'retained_task_entries': len(inventory['entries']),
        'task_content_sha256': _content_hash(inventory['entries']), 'materialization_policy': POLICY,
        'study_eligible': False}
    return seal_capture_json(output, 'input.json', receipt)


@contextmanager
def _input(custody, expected_input_sha256, max_receipt_bytes):
    _digest(expected_input_sha256); _positive(max_receipt_bytes, 'receipt byte limit')
    custody = Path(custody)
    _require(custody.is_absolute() and custody.parent.resolve() == custody.parent, 'input custody parent must be resolved')
    reader = _Reader(max_receipt_bytes)
    with _open(None, custody, directory=True) as root:
        receipt = reader.receipt(root, 'input.json', expected_input_sha256, 'caplab.task-input/v1')
        source = receipt.get('source_root')
        _require(isinstance(source, str) and source.startswith('/') and not source.startswith('//') and
                 source != '/' and '\0' not in source and str(PurePosixPath(source)) == source and
                 '..' not in PurePosixPath(source).parts, 'invalid task input source path')
        byte_limit = _positive(receipt.get('max_task_bytes'), 'task byte limit')
        entry_limit = _positive(receipt.get('max_task_entries'), 'task entry limit')
        _require(receipt.get('materialization_policy') == POLICY and receipt.get('study_eligible') is False,
                 'unsupported task input policy or eligibility assertion')
        with _open(root, 'inventory', directory=True) as objects:
            inventory = reader.receipt(objects, 'inventory.json', receipt.get('inventory_sha256'), 'caplab.task-inventory/v1')
            size, count = _inventory(objects, inventory, cwd=source, bytes_left=byte_limit, entries_left=entry_limit)
            _policy(inventory['entries'])
            _require(_count(receipt.get('retained_task_bytes'), 'retained bytes') == size and
                     _count(receipt.get('retained_task_entries'), 'retained entries') == count and
                     receipt.get('task_content_sha256') == _content_hash(inventory['entries']), 'task input summary differs')
            yield root, objects, receipt, inventory, max_receipt_bytes - reader.remaining


def verify_task_input(custody: Path, *, expected_input_sha256: str, max_receipt_bytes: int) -> dict:
    """Verify anchored input bytes without opening the original source or writing."""
    with _input(custody, expected_input_sha256, max_receipt_bytes) as (_, _, receipt, _, read_bytes):
        return {'schema': 'caplab.task-input-inspection/v1', 'input_sha256': expected_input_sha256,
            'integrity_verified': True, 'task_content_sha256': receipt['task_content_sha256'],
            'retained_task_bytes': receipt['retained_task_bytes'], 'retained_task_entries': receipt['retained_task_entries'],
            'verified_receipt_bytes': read_bytes, 'study_eligible': False}


@contextmanager
def _parent(root, path):
    descriptor = os.dup(root)
    try:
        for component in path.split('/')[:-1]:
            child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
            os.close(descriptor); descriptor = child
        yield descriptor, path.rpartition('/')[2]
    finally:
        os.close(descriptor)


def _ancestor(ancestor, child):
    descriptor, seen = os.dup(child), set()
    try:
        while True:
            info = os.fstat(descriptor); identity = (info.st_dev, info.st_ino)
            if identity == ancestor:
                return True
            if identity in seen:
                return False
            seen.add(identity)
            parent = os.open('..', os.O_PATH | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
            os.close(descriptor); descriptor = parent
    finally:
        os.close(descriptor)


def _copy_file(objects, entry, parent, name):
    with _open(objects, entry['object']) as source:
        before = os.fstat(source)
        target = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=parent)
        with os.fdopen(target, 'wb') as stream:
            copied, digest = 0, hashlib.sha256()
            while True:
                chunk = os.read(source, min(65536, entry['bytes'] - copied + 1))
                if not chunk:
                    break
                _require(copied + len(chunk) <= entry['bytes'], 'input object grew during materialization')
                stream.write(chunk); copied += len(chunk); digest.update(chunk)
            _require(copied == entry['bytes'] and digest.hexdigest() == entry['sha256'], 'input object changed during materialization')
            _unchanged(before, os.fstat(source), entry['object'])
            _unchanged(before, os.stat(entry['object'], dir_fd=objects, follow_symlinks=False), entry['object'])
            stream.flush(); os.fchmod(stream.fileno(), entry['mode']); os.fsync(stream.fileno())


def _verify_tree(root, entries):
    children = {e['path']: [] for e in entries if e['kind'] == 'directory'}
    for entry in entries:
        if entry['path'] != '.':
            children[entry['path'].rpartition('/')[0] or '.'].append(entry)
    def visit(parent, name, entry):
        before = os.stat(name, dir_fd=parent, follow_symlinks=False)
        kind = entry['kind']
        matches = {'directory': stat.S_ISDIR, 'file': stat.S_ISREG, 'symlink': stat.S_ISLNK}[kind]
        _require(matches(before.st_mode) and stat.S_IMODE(before.st_mode) == entry['mode'], 'materialized kind or mode differs')
        if kind == 'directory':
            with _open(parent, name, directory=True) as fd:
                _unchanged(before, os.fstat(fd), entry['path'])
                expected = children[entry['path']]
                names = sorted(e['path'].rpartition('/')[2] for e in expected)
                _require(_names(fd, len(names), 'unexpected materialized entry') == names, 'materialized children differ')
                for child in expected: visit(fd, child['path'].rpartition('/')[2], child)
                _require(_names(fd, len(names), 'unexpected materialized entry') == names, 'materialized children changed')
                _unchanged(before, os.fstat(fd), entry['path'])
        elif kind == 'file':
            _, size, sha = _read_file(parent, name, entry['bytes'], retain=False)
            _require((size, sha) == (entry['bytes'], entry['sha256']), 'materialized bytes differ')
        else:
            _require(os.fsencode(os.readlink(name, dir_fd=parent)) == base64.b64decode(entry['target_base64']),
                     'materialized symlink target differs')
        _unchanged(before, os.stat(name, dir_fd=parent, follow_symlinks=False), entry['path'])
    visit(root, '.', next(entry for entry in entries if entry['path'] == '.'))


def materialize_task_input(custody: Path, descriptor: int, *, expected_input_sha256: str,
                           expected_device: int, expected_inode: int, max_receipt_bytes: int) -> dict:
    """Create and verify a task in a borrowed, empty directory; retain partial effects on error.

    Caller owns authorization, blocked writers, stable ancestry and independent
    anchors. The returned receipt must be sealed by that caller before release.
    This does not attest a namespace path or preserve arbitrary filesystem metadata.
    """
    _require(all(type(v) is int and v >= 0 for v in (descriptor, expected_device, expected_inode)) and expected_inode > 0,
             'invalid task destination identity')
    target = os.dup(descriptor)
    try:
        info = os.fstat(target); identity = (expected_device, expected_inode)
        _require(stat.S_ISDIR(info.st_mode) and (info.st_dev, info.st_ino) == identity, 'task destination identity differs')
        with _input(custody, expected_input_sha256, max_receipt_bytes) as (root, objects, receipt, inventory, _):
            source = os.fstat(root)
            _require(not _ancestor((source.st_dev, source.st_ino), target) and not _ancestor(identity, root),
                     'task destination overlaps input custody')
            _require(_names(target, 0, 'task destination must be empty') == [], 'task destination must be empty')
            entries = inventory['entries']
            for entry in entries:
                if entry['path'] == '.':
                    continue
                with _parent(target, entry['path']) as (parent, name):
                    if entry['kind'] == 'directory':
                        os.mkdir(name, mode=0o700, dir_fd=parent)
                    elif entry['kind'] == 'file':
                        _copy_file(objects, entry, parent, name)
                    else:
                        os.symlink(base64.b64decode(entry['target_base64']), os.fsencode(name), dir_fd=parent)
            for entry in reversed(entries):
                if entry['kind'] == 'directory':
                    with _parent(target, entry['path']) as (parent, name):
                        with _open(parent, name, directory=True) as fd:
                            os.fchmod(fd, entry['mode']); os.fsync(fd)
            _verify_tree(target, entries)
            final = os.fstat(target)
            _require((final.st_dev, final.st_ino) == identity, 'task destination changed identity')
            return {'schema': 'caplab.task-input-materialization/v1', 'input_sha256': expected_input_sha256,
                'task_content_sha256': receipt['task_content_sha256'],
                'destination_identity': {'device': expected_device, 'inode': expected_inode},
                'materialized_bytes': receipt['retained_task_bytes'], 'materialized_entries': receipt['retained_task_entries'],
                'tree_verified': True, 'study_eligible': False}
    finally:
        os.close(target)
