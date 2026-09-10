import asyncio, json, hashlib, socket, threading, time, tempfile, unittest
from pathlib import Path
import test_scripted_native_protocol as existing

fixture = existing.fixture
payload = existing.payload


class HandshakeTests(unittest.IsolatedAsyncioTestCase):
    async def exercise(self, ack, *, deadline=30, delay=0.03, expired=False):
        with tempfile.TemporaryDirectory(
            prefix="caplab-native-freeze-protocol-"
        ) as temporary:
            path = str(Path(temporary) / "observer.sock")
            failures = []
            packets = []
            with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as listener:
                listener.bind(path)
                listener.listen(1)
                listener.settimeout(2)
                async with fixture.Fixture(
                    payload.scripted_response,
                    observation_socket=path,
                    deadline_seconds=deadline,
                ) as server:

                    def supervisor():
                        try:
                            channel, _ = listener.accept()
                            with channel:
                                channel.settimeout(2)
                                packets.append(channel.recv(65))
                                assert server.generated == 0 and all(
                                    "events_artifact" not in m for m in server.messages
                                )
                                time.sleep(delay)
                                assert server.generated == 0 and all(
                                    "events_artifact" not in m for m in server.messages
                                )
                                if ack:
                                    channel.sendall(ack)
                        except Exception as error:
                            failures.append(repr(error))

                    thread = threading.Thread(target=supervisor)
                    thread.start()
                    try:
                        async with existing.connect(
                            server.uri, compression=None, proxy=None
                        ) as ws:
                            if ack == b"1" and not expired:
                                first = await existing.response(ws, existing.TOOLS)
                                await existing.response(ws, existing.RESULT)
                                self.assertEqual(
                                    first[-1]["response"]["id"], "resp_caplab_1"
                                )
                            else:
                                await ws.send(json.dumps(existing.TOOLS))
                                with self.assertRaises(existing.ConnectionClosed):
                                    await asyncio.wait_for(ws.recv(), 2)
                        await asyncio.wait_for(server.done.wait(), 2)
                    finally:
                        thread.join(2)
                        self.assertFalse(thread.is_alive())
                        self.assertEqual(failures, [])
                    self.assertEqual(
                        packets,
                        [
                            hashlib.sha256(json.dumps(existing.TOOLS).encode())
                            .hexdigest()
                            .encode()
                        ],
                    )
                    if ack == b"1" and not expired:
                        self.assertEqual(server.generated, 2)
                        self.assertEqual(server.errors, [])
                        self.assertEqual(
                            sum(
                                "child_observation_requested_monotonic_ns" in x
                                for x in server.messages
                            ),
                            1,
                        )
                        first = server.messages[0]
                        self.assertLessEqual(
                            first["child_observation_requested_monotonic_ns"],
                            first["child_observation_acknowledged_monotonic_ns"],
                        )
                        self.assertLessEqual(
                            first["child_observation_acknowledged_monotonic_ns"],
                            first["written_monotonic_ns"],
                        )
                    else:
                        self.assertEqual(server.generated, 0)
                        self.assertTrue(server.errors)
                        self.assertTrue(
                            all("events_artifact" not in x for x in server.messages)
                        )

    async def test_single_handshake_precedes_both_scripted_responses(self):
        await self.exercise(b"1")

    async def test_bad_truncated_and_missing_ack_emit_no_response(self):
        for ack in [b"0", b"11", b""]:
            with self.subTest(ack=ack):
                await self.exercise(ack)

    async def test_original_fixture_deadline_still_applies(self):
        await self.exercise(b"1", deadline=0.05, delay=0.1, expired=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
