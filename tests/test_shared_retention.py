"""Real competing immutable publications; no fabricated SDK replies."""
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from caplab.revbench.shared_admission import _retain
from caplab.revbench.custody import LiveExecutionCustodyError


class SharedRetentionTests(unittest.TestCase):
    def compete(self, payloads):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            worker = root / 'writer.py'
            worker.write_text('import json,os,pathlib,sys,time\n'
                'from caplab.revbench.shared_admission import _retain\n'
                'root=pathlib.Path(sys.argv[1]); real=os.link\n'
                'def barrier(src,dst,*a,**kw):\n'
                ' if dst=="receipt.json":\n'
                '  (root/("ready-"+sys.argv[2])).touch()\n'
                '  end=time.monotonic()+10\n'
                '  while not (root/"release").exists():\n'
                '   if time.monotonic()>end: raise TimeoutError("publication barrier")\n'
                '   time.sleep(.01)\n'
                ' return real(src,dst,*a,**kw)\n'
                'os.link=barrier\n'
                '_retain(root,"receipt.json",json.loads(sys.argv[3]))\n')
            children = [subprocess.Popen([sys.executable, str(worker), str(root), str(i), json.dumps(d)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE) for i, d in enumerate(payloads)]
            try:
                end = time.monotonic() + 10
                while len(list(root.glob('ready-*'))) != 2 and time.monotonic() < end:
                    self.assertTrue(all(p.poll() is None for p in children))
                    time.sleep(.01)
                self.assertEqual(len(list(root.glob('ready-*'))), 2)
                (root / 'release').touch()
                replies = [p.communicate(timeout=10) for p in children]
                return [p.returncode for p in children], replies, (root / 'receipt.json').read_bytes()
            finally:
                for child in children:
                    if child.poll() is None:
                        child.kill()
                    child.communicate()

    def test_equal_concurrent_publications_both_return_same_complete_preimage(self):
        codes, replies, body = self.compete([{'value': 'same'}, {'value': 'same'}])
        self.assertEqual(codes, [0, 0], replies)
        self.assertEqual(body, b'{"value":"same"}')

    def test_conflicting_concurrent_publication_refuses_without_overwriting_winner(self):
        codes, replies, body = self.compete([{'value': 'A'}, {'value': 'B'}])
        self.assertEqual(sum(c == 0 for c in codes), 1, replies)
        self.assertTrue(any(b'shared_admission_custody_conflict' in r[1] for r in replies), replies)
        self.assertIn(body, [b'{"value":"A"}', b'{"value":"B"}'])

    def test_existing_symlink_is_not_an_idempotent_publication(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original = root / 'original'
            original.write_bytes(b'{"value":"same"}')
            (root / 'receipt.json').symlink_to(original)
            with self.assertRaises(LiveExecutionCustodyError):
                _retain(root, 'receipt.json', {'value': 'same'})
            self.assertEqual(original.read_bytes(), b'{"value":"same"}')
