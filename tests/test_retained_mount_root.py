"""Retained mount identity follows the root path, not filename ordering."""

import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from caplab.process_capture import seal_capture_json
from caplab.task_capture import _Inventory

SCRIPT = Path(__file__).resolve().parents[1]/'scripts/probe_cgroup_resource_limits.py'
spec = importlib.util.spec_from_file_location('resource_probe_root_test', SCRIPT)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class RetainedMountRootTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def test_writer_accepts_names_on_both_sides_of_root_sort_position(self):
        for index, name in enumerate(('ordinary', '!first', ' first', '#metadata')):
            with self.subTest(name=name):
                source = self.root/str(index)
                source.mkdir()
                (source/name).write_bytes(b'opaque\x00\xff')
                fd = os.open(source, os.O_RDONLY|os.O_DIRECTORY)
                try:
                    info = os.fstat(fd)
                    identity = {'source_root':'/work','source_dev':info.st_dev,'source_ino':info.st_ino}
                    output = self.root/(str(index)+'-retained')
                    digest, left, count = probe.retain_mount(fd, output, identity, 1000, 10)
                    receipt = json.loads((output/'inventory.json').read_bytes())
                    self.assertEqual(digest, probe.digest(output/'inventory.json'))
                    self.assertEqual([e['path'] for e in receipt['entries']], sorted(('.', name)))
                    file_entry, = (e for e in receipt['entries'] if e['path']==name)
                    self.assertEqual((output/file_entry['object']).read_bytes(), b'opaque\x00\xff')
                    self.assertEqual((left,count), (992,8))
                    self.assertEqual(os.fstat(fd).st_ino, info.st_ino)
                finally:
                    os.close(fd)

    def test_writer_rejects_child_identity_even_when_child_sorts_first(self):
        source = self.root/'source'
        source.mkdir()
        child = source/'!first'
        child.write_bytes(b'payload')
        fd = os.open(source, os.O_RDONLY|os.O_DIRECTORY)
        try:
            child_info = child.stat()
            identity = {'source_root':'/work','source_dev':child_info.st_dev,'source_ino':child_info.st_ino}
            output = self.root/'retained'
            with self.assertRaisesRegex(RuntimeError,'retained root identity differs'):
                probe.retain_mount(fd, output, identity, 1000, 10)
            self.assertFalse((output/'inventory.json').exists())
            self.assertEqual(os.fstat(fd).st_ino, source.stat().st_ino)
        finally:
            os.close(fd)

    def fixture(self, *, child_identity=False, through_writer=False):
        sources = self.root/'sources'
        sources.mkdir()
        retained = self.root/'fixture-retained'
        retained.mkdir()
        identities, inventories = [], []
        bytes_left, entries_left = 40*probe.MIB, 100
        for index, mount in enumerate(probe.MOUNTS):
            source = sources/str(index)
            source.mkdir()
            (source/'marker.bin').write_bytes(probe.MARKER+mount.encode('ascii'))
            child = source/'!first'
            child.write_bytes(b'non-root identity sentinel')
            fd = os.open(source, os.O_RDONLY|os.O_DIRECTORY)
            try:
                info = child.stat() if child_identity else os.fstat(fd)
                identity = {'source_root':mount,'source_dev':info.st_dev,'source_ino':info.st_ino}
                output = retained/str(index)
                if through_writer:
                    digest, bytes_left, entries_left = probe.retain_mount(
                        fd,output,identity,bytes_left,entries_left)
                else:
                    # Construct the verifier input without the writer under test.
                    output.mkdir()
                    inventory = _Inventory(output,bytes_left,entries_left)
                    inventory.visit(fd,'.','.')
                    receipt = {'schema':'caplab.retained-mount-inventory/v1',
                        'source_root':mount,'descriptor_identity':identity,
                        'max_retained_bytes':bytes_left,'max_entries':entries_left,
                        'retained_bytes':inventory.retained_bytes,
                        'entries':sorted(inventory.entries,key=lambda entry:entry['path'])}
                    digest = seal_capture_json(output,'inventory.json',receipt)
                    bytes_left, entries_left = inventory.bytes_left, inventory.entries_left
            finally:
                os.close(fd)
            identities.append(identity)
            inventories.append({'source_root':mount,'inventory_sha256':digest})
        shutil.rmtree(sources)
        return {'reports':[{'mode':'fixture','inventories':inventories,
            'mount_descriptor':{'mounts':identities},
            'retained_bytes':40*probe.MIB-bytes_left,'retained_entries':100-entries_left}]}

    def test_verifier_accepts_punctuation_names_after_source_removal(self):
        observation = self.fixture()
        probe.verify_retention(self.root,observation)
        self.assertFalse((self.root/'sources').exists())

    def test_verifier_rejects_consistent_child_identity_substitution(self):
        observation = self.fixture(child_identity=True)
        with self.assertRaisesRegex(RuntimeError,'retained root differs from handed-off mount'):
            probe.verify_retention(self.root,observation)

    def test_writer_and_verifier_round_trip_all_mounts_after_source_removal(self):
        observation = self.fixture(through_writer=True)
        probe.verify_retention(self.root,observation)
        self.assertFalse((self.root/'sources').exists())
