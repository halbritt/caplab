"""Synthetic retention failures and controlled concurrent publication."""

from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from pathlib import Path
import tempfile
import threading
import unittest
from unittest import mock

from caplab.advisory import cas


class AdvisoryCASRetentionTests(unittest.TestCase):
    def test_retain_refuses_existing_corruption_without_repairing_it(self):
        with tempfile.TemporaryDirectory() as root:
            digest = cas.retain("original", root=root)
            path = Path(root, digest[:2], digest)
            path.write_bytes(b"corrupt")
            before = path.stat()
            with self.assertRaises(ValueError):
                cas.retain("original", root=root)
            self.assertEqual(path.read_bytes(), b"corrupt")
            self.assertEqual(path.stat().st_ino, before.st_ino)
            self.assertEqual(path.stat().st_mtime_ns, before.st_mtime_ns)
            self.assertEqual(list(path.parent.iterdir()), [path])

    def test_identical_replay_preserves_bytes_and_object(self):
        for body in ("", "caf\u00e9\r\n\u2028end\n"):
            with self.subTest(body=body), tempfile.TemporaryDirectory() as root:
                digest = cas.retain(body, root=root)
                path = Path(root, digest[:2], digest)
                before = path.stat()
                self.assertEqual(digest, sha256(body.encode("utf-8")).hexdigest())
                self.assertEqual(cas.retain(body, root=root), digest)
                self.assertEqual(cas.load(digest, root=root), body)
                self.assertEqual(path.read_bytes(), body.encode("utf-8"))
                self.assertEqual(path.stat().st_ino, before.st_ino)
                self.assertEqual(path.stat().st_mtime_ns, before.st_mtime_ns)
                self.assertEqual(list(path.parent.iterdir()), [path])

    def test_same_content_writers_both_succeed(self):
        # Hold both writers immediately before publication. This exercises the
        # old rename and the replacement create-only link at the same boundary.
        barrier = threading.Barrier(2, timeout=5)
        real_replace, real_link = cas.os.replace, cas.os.link

        def publish(operation):
            def held(*args, **kwargs):
                barrier.wait()
                return operation(*args, **kwargs)
            return held

        with tempfile.TemporaryDirectory() as root, \
                mock.patch.object(cas.os, "replace", side_effect=publish(real_replace)), \
                mock.patch.object(cas.os, "link", side_effect=publish(real_link)):
            with ThreadPoolExecutor(max_workers=2) as pool:
                futures = [pool.submit(cas.retain, "same body", root=root) for _ in range(2)]
                results = [future.result(timeout=10) for future in futures]
            self.assertEqual(results[0], results[1])
            self.assertEqual(cas.load(results[0], root=root), "same body")
            path = Path(root, results[0][:2], results[0])
            self.assertEqual(list(path.parent.iterdir()), [path])

    def test_conflicting_destination_appearing_at_publication_is_preserved(self):
        real_replace, real_link = cas.os.replace, cas.os.link

        def race(operation):
            def appeared(source, destination, **kwargs):
                Path(destination).write_bytes(b"conflicting retained bytes")
                return operation(source, destination, **kwargs)
            return appeared

        with tempfile.TemporaryDirectory() as root, \
                mock.patch.object(cas.os, "replace", side_effect=race(real_replace)), \
                mock.patch.object(cas.os, "link", side_effect=race(real_link)):
            with self.assertRaises(ValueError):
                cas.retain("intended", root=root)
            digest = sha256(b"intended").hexdigest()
            path = Path(root, digest[:2], digest)
            self.assertEqual(path.read_bytes(), b"conflicting retained bytes")
            self.assertEqual(list(path.parent.iterdir()), [path])

    def test_failed_stage_sync_does_not_publish_or_leave_temporary_bytes(self):
        with tempfile.TemporaryDirectory() as root, \
                mock.patch.object(cas.os, "fsync", side_effect=OSError("synthetic sync failure")):
            with self.assertRaisesRegex(OSError, "synthetic sync failure"):
                cas.retain("unpublished", root=root)
            self.assertEqual([p for p in Path(root).rglob("*") if p.is_file()], [])

    def test_primary_source_load_does_not_hide_failed_retention(self):
        from caplab.advisory.calibrate import load_substrate_body

        with tempfile.TemporaryDirectory() as directory:
            root = str(Path(directory, "cas"))
            digest = cas.retain("primary body", root=root)
            retained = Path(root, digest[:2], digest)
            retained.write_bytes(b"corrupt")
            exchange = Path(directory, "exchange")
            primary = exchange / "dispatch/synthetic/input.md"
            primary.parent.mkdir(parents=True)
            primary.write_bytes(b"primary body")
            case = {"sha256": digest, "source": {
                "kind": "striatum-exchange", "dispatch_id": "synthetic",
                "input_path": "input.md",
            }}
            with mock.patch.object(cas, "DEFAULT_ROOT", root), \
                    self.assertRaises(ValueError):
                load_substrate_body(case, exchange_root=str(exchange), repos={})
            self.assertEqual(retained.read_bytes(), b"corrupt")
            self.assertEqual(primary.read_bytes(), b"primary body")


if __name__ == "__main__":
    unittest.main()
