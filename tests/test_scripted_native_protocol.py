import asyncio, json, os, tempfile, unittest
from pathlib import Path
import sys

package = os.environ.get("CAPLAB_TEST_WEBSOCKETS_ROOT")
if package:
    sys.path.insert(0, str(Path(package).parent))
try:
    import websockets
except ModuleNotFoundError as error:
    if error.name != "websockets":
        raise
    raise unittest.SkipTest(
        "requires websockets 15.0.1; set CAPLAB_TEST_WEBSOCKETS_ROOT"
    )
from websockets.exceptions import ConnectionClosed, InvalidStatus
from websockets.asyncio.client import connect

import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
from scripted_native import payload, fixture

IDENTITY = {"model": "gpt-5.6-terra", "effort": "max", "summary": "detailed"}
REQUEST_IDENTITY = {
    "model": IDENTITY["model"],
    "reasoning": {"effort": IDENTITY["effort"], "summary": IDENTITY["summary"]},
}
from functools import partial

fixed_fixture = partial(fixture.Fixture, expected_identity=IDENTITY)

TOOLS = {
    **REQUEST_IDENTITY,
    "type": "response.create",
    "input": [
        {
            "tools": [
                {
                    "type": "namespace",
                    "name": "functions",
                    "tools": [
                        {
                            "type": "custom",
                            "name": "exec",
                            "description": "tools.exec_command",
                            "format": {"type": "text"},
                        }
                    ],
                }
            ]
        }
    ],
}
RESULT = {
    **REQUEST_IDENTITY,
    "type": "response.create",
    "previous_response_id": "resp_caplab_1",
    "input": [
        {
            "type": "custom_tool_call_output",
            "call_id": "call_caplab_fixed",
            "output": payload.WITNESS,
        }
    ],
}


async def response(ws, document):
    await ws.send(json.dumps(document))
    events = []
    while True:
        event = json.loads(await asyncio.wait_for(ws.recv(), 2))
        events.append(event)
        if event["type"] == "response.completed":
            return events


class Controls(unittest.IsolatedAsyncioTestCase):
    async def test_identity_is_required_on_warmup_and_every_generated_turn(self):
        from copy import deepcopy

        mutations = [
            {"model": None},
            {"model": 1},
            {"model": "other"},
            {"reasoning": None},
            {"reasoning": []},
            {"reasoning": "max"},
            {"reasoning": {}},
            {"reasoning": {"effort": "low", "summary": "detailed"}},
            {"reasoning": {"effort": "max"}},
            {"reasoning": {"effort": "max", "summary": False}},
            {"reasoning": {"effort": "max", "summary": "auto"}},
        ]
        for stage in ("first", "warmup", "after-warmup", "tool-result"):
            for mutation in mutations:
                with self.subTest(stage=stage, mutation=mutation):
                    async with fixed_fixture(payload.scripted_response) as server:
                        async with connect(
                            server.uri, compression=None, proxy=None
                        ) as ws:
                            document = deepcopy(
                                RESULT if stage == "tool-result" else TOOLS
                            )
                            if stage == "warmup":
                                document["generate"] = False
                            elif stage == "after-warmup":
                                warmup = await response(ws, TOOLS | {"generate": False})
                                document["previous_response_id"] = warmup[-1][
                                    "response"
                                ]["id"]
                                document["input"] = []
                            elif stage == "tool-result":
                                await response(ws, TOOLS)
                            document.update(mutation)
                            # Null and absent are both required-field failures.
                            for field in ("model", "reasoning"):
                                if document.get(field) is None:
                                    document.pop(field, None)
                            before = server.generated
                            await ws.send(json.dumps(document))
                            with self.assertRaises(ConnectionClosed):
                                await asyncio.wait_for(ws.recv(), 2)
                        await asyncio.wait_for(server.done.wait(), 2)
                        self.assertEqual(server.generated, before)
                        self.assertTrue(server.stop_required)
                        self.assertIn("request ", server.errors[0])
                        self.assertNotIn("events_artifact", server.messages[-1])
                        self.assertNotIn("written_monotonic_ns", server.messages[-1])

    async def test_identity_refusal_precedes_the_child_observation_handshake(self):
        with tempfile.TemporaryDirectory() as temporary:
            async with fixed_fixture(
                payload.scripted_response,
                observation_socket=str(Path(temporary) / "absent.sock"),
            ) as server:
                async with connect(server.uri, compression=None, proxy=None) as ws:
                    await ws.send(
                        json.dumps(TOOLS | {"model": "other", "generate": False})
                    )
                    with self.assertRaises(ConnectionClosed):
                        await asyncio.wait_for(ws.recv(), 2)
                await asyncio.wait_for(server.done.wait(), 2)
                self.assertIn("request model differs", server.errors[0])
                self.assertNotIn(
                    "child_observation_requested_monotonic_ns", server.messages[0]
                )

    async def test_expected_identity_is_copied_and_additional_reasoning_is_retained(
        self,
    ):
        expected = dict(IDENTITY)
        document = TOOLS | {
            "reasoning": REQUEST_IDENTITY["reasoning"] | {"context": "all_turns"}
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "requests"
            async with fixture.Fixture(
                payload.scripted_response, expected_identity=expected, capture_dir=root
            ) as server:
                expected["model"] = "changed after construction"
                async with connect(server.uri, compression=None, proxy=None) as ws:
                    await response(ws, document)
                    await response(ws, RESULT)
                await asyncio.wait_for(server.done.wait(), 2)
                self.assertEqual(server.errors, [])
                self.assertEqual(server.messages[0]["request_identity"], IDENTITY)
                self.assertEqual(
                    json.loads((root / "0.request.json").read_bytes()), document
                )
        for invalid in (
            {},
            IDENTITY | {"extra": "x"},
            IDENTITY | {"effort": False},
            IDENTITY | {"model": ""},
            IDENTITY | {"summary": "x" * 257},
        ):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                fixture.Fixture(payload.scripted_response, expected_identity=invalid)

    async def test_off_pin_request_is_retained_without_a_scripted_response(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "requests"
            async with fixed_fixture(
                payload.scripted_response, capture_dir=root
            ) as server:
                async with connect(server.uri, compression=None, proxy=None) as ws:
                    raw = json.dumps(TOOLS | {"model": "different-model"})
                    await ws.send(raw)
                    with self.assertRaises(ConnectionClosed):
                        await asyncio.wait_for(ws.recv(), 2)
                await asyncio.wait_for(server.done.wait(), 2)
                self.assertEqual(server.generated, 0)
                self.assertIn("request model differs", server.errors[0])
                self.assertEqual((root / "0.request.json").read_bytes(), raw.encode())
                self.assertFalse((root / "0.events.jsonl").exists())

    async def test_fixed_exchange_preserves_scripted_events_and_closes(self):
        async with fixed_fixture(payload.scripted_response) as server:
            async with connect(server.uri, compression=None, proxy=None) as ws:
                first = await response(ws, TOOLS)
                second = await response(ws, RESULT)
                self.assertEqual(
                    first,
                    [
                        json.loads(line[6:])
                        for line in payload.scripted_response(TOOLS, 1).splitlines()
                        if line.startswith(b"data: ")
                    ],
                )
                self.assertEqual(
                    second,
                    [
                        json.loads(line[6:])
                        for line in payload.scripted_response(RESULT, 2).splitlines()
                        if line.startswith(b"data: ")
                    ],
                )
                self.assertEqual(
                    second[-1]["response"]["output"][0]["content"][0]["text"],
                    payload.FINAL,
                )
            await asyncio.wait_for(server.done.wait(), 2)
            self.assertEqual(server.errors, [])
            self.assertEqual(server.generated, 2)
        self.assertTrue(server.closed)

    async def test_warmup_retains_context_and_requires_its_response_id(self):
        async with fixed_fixture(payload.scripted_response) as server:
            async with connect(server.uri, compression=None, proxy=None) as ws:
                warmup = await response(ws, TOOLS | {"generate": False})
                self.assertEqual(warmup[-1]["response"]["output"], [])
                first = await response(
                    ws,
                    {
                        **REQUEST_IDENTITY,
                        "type": "response.create",
                        "previous_response_id": warmup[-1]["response"]["id"],
                        "input": [],
                    },
                )
                self.assertEqual(
                    first[-1]["response"]["output"][0]["input"], payload.TOOL_JAVASCRIPT
                )
                await response(ws, RESULT)
            await asyncio.wait_for(server.done.wait(), 2)
            self.assertEqual(server.errors, [])
            self.assertEqual(server.generated, 2)

    async def test_invalid_messages_emit_no_scripted_response(self):
        valid = json.dumps(TOOLS)
        cases = [
            json.dumps(TOOLS | {"type": "wrong"}),
            json.dumps(TOOLS | {"generate": 0}),
            valid.replace(
                '"type": "response.create"',
                '"type":"wrong","type":"response.create"',
                1,
            ),
            valid[:-1] + ',"extra":NaN}',
            valid.encode(),
            "{bad",
            "x" * (fixture.MAX_MESSAGE + 1),
        ]
        for raw in cases:
            with self.subTest(raw_type=type(raw).__name__, bytes=len(raw)):
                async with fixed_fixture(payload.scripted_response) as server:
                    async with connect(server.uri, compression=None, proxy=None) as ws:
                        await ws.send(raw)
                        with self.assertRaises(ConnectionClosed):
                            await asyncio.wait_for(ws.recv(), 2)
                    await asyncio.wait_for(server.done.wait(), 2)
                    self.assertTrue(server.errors)
                    self.assertEqual(server.generated, 0)

    async def test_rejects_second_connection_before_message_processing(self):
        async with fixed_fixture(payload.scripted_response) as server:
            async with connect(server.uri, compression=None, proxy=None) as first:
                with self.assertRaises(InvalidStatus) as caught:
                    async with connect(server.uri, compression=None, proxy=None):
                        pass
                self.assertEqual(caught.exception.response.status_code, 409)
                await response(first, TOOLS)
                await response(first, RESULT)
            await asyncio.wait_for(server.done.wait(), 2)
            self.assertEqual(server.generated, 2)

    async def test_lineage_wrong_result_and_extra_responses_are_refused(self):
        cases = [
            RESULT | {"previous_response_id": "wrong"},
            RESULT | {"previous_response_id": None},
            RESULT
            | {
                "input": [
                    {
                        "type": "custom_tool_call_output",
                        "call_id": "wrong",
                        "output": payload.WITNESS,
                    }
                ]
            },
            RESULT
            | {
                "input": [
                    {
                        "type": "custom_tool_call_output",
                        "call_id": "call_caplab_fixed",
                        "output": "wrong",
                    }
                ]
            },
            RESULT | {"generate": False},
        ]
        for document in cases:
            with self.subTest(document=document):
                async with fixed_fixture(payload.scripted_response) as server:
                    async with connect(server.uri, compression=None, proxy=None) as ws:
                        await response(ws, TOOLS)
                        await ws.send(json.dumps(document))
                        with self.assertRaises(ConnectionClosed):
                            await asyncio.wait_for(ws.recv(), 2)
                    await asyncio.wait_for(server.done.wait(), 2)
                    self.assertEqual(server.generated, 1)
                    self.assertTrue(server.errors)
        async with fixed_fixture(payload.scripted_response) as server:
            async with connect(server.uri, compression=None, proxy=None) as ws:
                await response(ws, TOOLS)
                await response(ws, RESULT)
                await ws.send(
                    json.dumps(RESULT | {"previous_response_id": "resp_caplab_2"})
                )
                with self.assertRaises(ConnectionClosed):
                    await asyncio.wait_for(ws.recv(), 2)
            await asyncio.wait_for(server.done.wait(), 2)
            self.assertEqual(server.generated, 2)
            self.assertTrue(server.errors)

    async def test_deadline_and_early_close_leave_no_success(self):
        async with fixed_fixture(
            payload.scripted_response, deadline_seconds=0.05
        ) as server:
            async with connect(server.uri, compression=None, proxy=None) as ws:
                with self.assertRaises(ConnectionClosed):
                    await asyncio.wait_for(ws.recv(), 2)
            await asyncio.wait_for(server.done.wait(), 2)
            self.assertTrue(any("TimeoutError" in e for e in server.errors))
            self.assertEqual(server.generated, 0)
        async with fixed_fixture(payload.scripted_response) as server:
            async with connect(server.uri, compression=None, proxy=None):
                pass
            await asyncio.wait_for(server.done.wait(), 2)
            self.assertEqual(server.errors, ["incomplete exchange"])

    async def test_http_routes_and_active_connection_cleanup(self):
        before = set(os.listdir("/proc/self/fd"))
        async with fixed_fixture(payload.scripted_response) as server:
            port = int(server.uri.split(":")[2].split("/")[0])
            reader, writer = await asyncio.open_connection("127.0.0.1", port)
            writer.write(
                b"GET /__fixture_check HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
            )
            await writer.drain()
            raw = await asyncio.wait_for(reader.read(), 2)
            writer.close()
            await writer.wait_closed()
            self.assertIn(b"200 OK", raw)
            self.assertTrue(raw.endswith(b'{"fixture":true}'))
            with self.assertRaises(InvalidStatus) as caught:
                async with connect(
                    server.uri.replace("/responses", "/wrong"),
                    compression=None,
                    proxy=None,
                ):
                    pass
            self.assertEqual(caught.exception.response.status_code, 404)
            ws = await connect(server.uri, compression=None, proxy=None)
        with self.assertRaises(ConnectionClosed):
            await ws.recv()
        await ws.close()
        self.assertTrue(server.closed)
        self.assertEqual(set(os.listdir("/proc/self/fd")), before)
        with self.assertRaises(OSError):
            await asyncio.open_connection("127.0.0.1", port)

    async def test_warmup_cannot_be_repeated(self):
        async with fixed_fixture(payload.scripted_response) as server:
            async with connect(server.uri, compression=None, proxy=None) as ws:
                await response(ws, TOOLS | {"generate": False})
                await ws.send(
                    json.dumps(
                        TOOLS
                        | {
                            "generate": False,
                            "previous_response_id": "resp_caplab_warmup",
                        }
                    )
                )
                with self.assertRaises(ConnectionClosed):
                    await asyncio.wait_for(ws.recv(), 2)
            await asyncio.wait_for(server.done.wait(), 2)
            self.assertEqual(server.generated, 0)
            self.assertTrue(server.errors)

    async def test_raw_exchange_is_retained_before_response(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "capture"
            async with fixed_fixture(
                payload.scripted_response, capture_dir=root
            ) as server:
                async with connect(server.uri, compression=None, proxy=None) as ws:
                    first = await response(ws, TOOLS)
                    self.assertEqual(
                        (root / "0.request.json").read_bytes(),
                        json.dumps(TOOLS).encode(),
                    )
                    self.assertEqual(
                        [
                            json.loads(l)
                            for l in (root / "0.events.jsonl").read_text().splitlines()
                        ],
                        first,
                    )
                    await response(ws, RESULT)
                await asyncio.wait_for(server.done.wait(), 2)
                self.assertEqual(server.errors, [])
            self.assertEqual(len(list(root.iterdir())), 4)

    async def test_request_retention_failure_prevents_response(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "capture"
            async with fixed_fixture(
                payload.scripted_response, capture_dir=root
            ) as server:
                (root / "0.request.json").write_bytes(b"preserve")
                async with connect(server.uri, compression=None, proxy=None) as ws:
                    await ws.send(json.dumps(TOOLS))
                    with self.assertRaises(ConnectionClosed):
                        await asyncio.wait_for(ws.recv(), 2)
                await asyncio.wait_for(server.done.wait(), 2)
                self.assertEqual(server.generated, 0)
                self.assertTrue(any("FileExistsError" in e for e in server.errors))
                self.assertEqual((root / "0.request.json").read_bytes(), b"preserve")

    async def test_ancillary_post_refusal_is_observed_and_ws_still_works(self):
        async with fixed_fixture(payload.scripted_response) as server:
            port = int(server.uri.split(":")[2].split("/")[0])
            reader, writer = await asyncio.open_connection("127.0.0.1", port)
            writer.write(
                b"POST /api/codex/ps/mcp HTTP/1.1\r\nHost: localhost\r\nContent-Length: 2\r\nConnection: close\r\n\r\n{}"
            )
            await writer.drain()
            raw = await asyncio.wait_for(reader.read(), 2)
            writer.close()
            await writer.wait_closed()
            self.assertTrue(raw.startswith(b"HTTP/1.1 404 Not Found"))
            self.assertEqual(len(server.library_events), 1)
            self.assertEqual(
                server.library_events[0]["classification"], "handled-http-post"
            )
            self.assertEqual(server.errors, [])
            async with connect(server.uri, compression=None, proxy=None) as ws:
                await response(ws, TOOLS)
                await response(ws, RESULT)
            await asyncio.wait_for(server.done.wait(), 2)
            self.assertEqual(server.errors, [])

    async def test_http_post_bounds_and_response_fallback_refusal(self):
        cases = [
            b"Content-Length: 0\r\nContent-Length: 0",
            b"Transfer-Encoding: chunked\r\nContent-Length: 0",
            b"Content-Length: 1048577",
            b"Content-Length: -1",
            b"Content-Length: 0\r\nX-Long: " + b"x" * 16384,
        ]
        for headers in cases:
            async with fixed_fixture(payload.scripted_response) as server:
                port = int(server.uri.split(":")[2].split("/")[0])
                reader, writer = await asyncio.open_connection("127.0.0.1", port)
                writer.write(b"POST /other HTTP/1.1\r\n" + headers + b"\r\n\r\n")
                await writer.drain()
                raw = await asyncio.wait_for(reader.read(), 2)
                writer.close()
                await writer.wait_closed()
                self.assertTrue(raw.startswith(b"HTTP/1.1 400 Bad Request"), raw)
                self.assertTrue(server.errors)
                self.assertEqual(server.generated, 0)
        async with fixed_fixture(payload.scripted_response) as server:
            port = int(server.uri.split(":")[2].split("/")[0])
            reader, writer = await asyncio.open_connection("127.0.0.1", port)
            for part in [
                b"PO",
                b"ST /responses HTTP/1.1\r\nContent-Length: 2\r\n\r\n{",
                b"}",
            ]:
                writer.write(part)
                await writer.drain()
                await asyncio.sleep(0)
            raw = await asyncio.wait_for(reader.read(), 2)
            writer.close()
            await writer.wait_closed()
            self.assertTrue(raw.startswith(b"HTTP/1.1 405 Method Not Allowed"), raw)
            self.assertIn("unexpected HTTP response fallback", server.errors)
            self.assertEqual(server.http_requests[0]["body_bytes"], 2)

    async def test_incomplete_post_and_event_retention_fail_closed(self):
        async with fixed_fixture(payload.scripted_response) as server:
            port = int(server.uri.split(":")[2].split("/")[0])
            reader, writer = await asyncio.open_connection("127.0.0.1", port)
            writer.write(b"POST /other HTTP/1.1\r\nContent-Length: 2\r\n\r\n{")
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            await asyncio.sleep(0.02)
            self.assertIn("incomplete HTTP POST", server.errors)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "capture"
            async with fixed_fixture(
                payload.scripted_response, capture_dir=root
            ) as server:
                (root / "0.events.jsonl").write_bytes(b"preserve")
                async with connect(server.uri, compression=None, proxy=None) as ws:
                    await ws.send(json.dumps(TOOLS))
                    with self.assertRaises(ConnectionClosed):
                        await asyncio.wait_for(ws.recv(), 2)
                await asyncio.wait_for(server.done.wait(), 2)
                self.assertTrue(server.errors)
                self.assertEqual((root / "0.events.jsonl").read_bytes(), b"preserve")
                self.assertNotIn("written_monotonic_ns", server.messages[0])


class ShutdownControls(unittest.IsolatedAsyncioTestCase):
    async def test_abort_after_complete_responses_preserves_error_without_stop(self):
        async with fixed_fixture(payload.scripted_response) as server:
            ws = await connect(server.uri, compression=None, proxy=None)
            await response(ws, TOOLS)
            await response(ws, RESULT)
            ws.transport.abort()
            await asyncio.wait_for(server.done.wait(), 2)
            self.assertEqual(
                server.errors,
                ["ConnectionClosedError: no close frame received or sent"],
            )
            self.assertFalse(server.stop_required)
            self.assertEqual(server.deferred_close["error_index"], 0)
            self.assertEqual(server.deferred_close["generated_responses"], 2)
            self.assertGreaterEqual(
                server.deferred_close["observed_monotonic_ns"],
                server.messages[-1]["written_monotonic_ns"],
            )
            self.assertIsNone(server.deferred_close["received_close_code"])
            self.assertIsNone(server.deferred_close["sent_close_code"])

    async def test_bootstrap_worker_defers_close_but_stops_for_later_fallback(self):
        import sys, threading

        with tempfile.TemporaryDirectory() as tmp:
            import ast

            tree = ast.parse(
                (REPO / "scripts/scripted_native/bootstrap.py").read_text()
            )
            start = next(
                i
                for i, node in enumerate(tree.body)
                if isinstance(node, ast.Import)
                and any(alias.name == "asyncio" for alias in node.names)
            )
            end = next(
                i
                for i, node in enumerate(tree.body[start:], start)
                if isinstance(node, ast.Assign)
                and any(
                    isinstance(t, ast.Name) and t.id == "process" for t in node.targets
                )
            )
            code_root = str(REPO / "scripts/scripted_native")
            replacements = {
                "/fixture-code": code_root,
                "/fixture-code/guard.py": code_root + "/guard.py",
                "/fixture-deps": str(Path(websockets.__file__).parent.parent),
                "/episode/fixture-requests": tmp + "/requests",
                "/child-observation.sock": None,
            }

            class LocalPaths(ast.NodeTransformer):
                def visit_Constant(self, node):
                    if isinstance(node.value, str) and node.value in replacements:
                        return ast.copy_location(
                            ast.Constant(replacements[node.value]), node
                        )
                    return node

            source = ast.fix_missing_locations(
                LocalPaths().visit(
                    ast.Module(body=tree.body[start:end], type_ignores=[])
                )
            )
            namespace = {
                "sys": sys,
                "plan": {
                    "base_subject": {
                        "model_id": IDENTITY["model"],
                        "effort": IDENTITY["effort"],
                    }
                },
                "threading": threading,
                "Path": Path,
                "scripted_response": payload.scripted_response,
            }
            exec(compile(source, "actual-fixture-worker", "exec"), namespace)
            try:
                uri = "ws://127.0.0.1:" + str(namespace["state"]["port"]) + "/responses"
                ws = await connect(uri, compression=None, proxy=None)
                await response(ws, TOOLS)
                await response(ws, RESULT)
                ws.transport.abort()
                for _ in range(100):
                    if namespace["errors"]:
                        break
                    await asyncio.sleep(0.01)
                self.assertEqual(
                    namespace["errors"],
                    ["ConnectionClosedError: no close frame received or sent"],
                )
                await asyncio.sleep(0.1)
                self.assertFalse(namespace["stop_event"].is_set())
                self.assertIsNone(namespace["stop_reason"])
                reader, writer = await asyncio.open_connection(
                    "127.0.0.1", namespace["state"]["port"]
                )
                writer.write(b"POST /responses HTTP/1.1\r\nContent-Length: 0\r\n\r\n")
                await writer.drain()
                self.assertIn(
                    b"405 Method Not Allowed", await asyncio.wait_for(reader.read(), 2)
                )
                writer.close()
                await writer.wait_closed()
                for _ in range(100):
                    if namespace["stop_event"].is_set():
                        break
                    await asyncio.sleep(0.01)
                self.assertTrue(namespace["stop_event"].is_set())
                self.assertEqual(namespace["stop_reason"], "fixture_error")
                self.assertEqual(len(namespace["errors"]), 2)
            finally:
                namespace["stop_event"].set()
                namespace["thread"].join(timeout=3)
                self.assertFalse(namespace["thread"].is_alive())

    async def test_early_abort_and_non_normal_close_codes_still_stop(self):
        for generated in [0, 1, 2]:
            with self.subTest(generated=generated):
                async with fixed_fixture(payload.scripted_response) as server:
                    ws = await connect(server.uri, compression=None, proxy=None)
                    if generated >= 1:
                        await response(ws, TOOLS)
                    if generated == 2:
                        await response(ws, RESULT)
                        await ws.close(code=1002, reason="test protocol failure")
                    else:
                        ws.transport.abort()
                    await asyncio.wait_for(server.done.wait(), 2)
                    self.assertTrue(server.stop_required)
                    self.assertIsNone(server.deferred_close)

    async def test_post_completion_malformed_input_still_stops(self):
        for raw_frame in [False, True]:
            with self.subTest(raw_frame=raw_frame):
                async with fixed_fixture(payload.scripted_response) as server:
                    ws = await connect(server.uri, compression=None, proxy=None)
                    await response(ws, TOOLS)
                    await response(ws, RESULT)
                    if raw_frame:
                        ws.transport.write(b"\x81\x00")
                    else:
                        await ws.send("{bad")
                    with self.assertRaises(ConnectionClosed):
                        await asyncio.wait_for(ws.recv(), 2)
                    await asyncio.wait_for(server.done.wait(), 2)
                    self.assertTrue(server.stop_required)
                    self.assertIsNone(server.deferred_close)
                    await ws.close()

    async def test_final_retention_failure_and_open_socket_deadline_still_stop(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "capture"
            async with fixed_fixture(
                payload.scripted_response, capture_dir=root
            ) as server:
                ws = await connect(server.uri, compression=None, proxy=None)
                await response(ws, TOOLS)
                (root / "1.events.jsonl").write_bytes(b"preserve")
                await ws.send(json.dumps(RESULT))
                with self.assertRaises(ConnectionClosed):
                    await asyncio.wait_for(ws.recv(), 2)
                await asyncio.wait_for(server.done.wait(), 2)
                self.assertEqual(server.generated, 2)
                self.assertNotIn("written_monotonic_ns", server.messages[-1])
                self.assertIsNone(server.deferred_close)
                self.assertTrue(server.stop_required)
                self.assertEqual((root / "1.events.jsonl").read_bytes(), b"preserve")
                await ws.close()
        async with fixed_fixture(
            payload.scripted_response, deadline_seconds=0.1
        ) as server:
            ws = await connect(server.uri, compression=None, proxy=None)
            await response(ws, TOOLS)
            await response(ws, RESULT)
            await asyncio.wait_for(server.done.wait(), 2)
            self.assertEqual(server.generated, 2)
            self.assertTrue(any("TimeoutError" in e for e in server.errors))
            self.assertIsNone(server.deferred_close)
            self.assertTrue(server.stop_required)
            await ws.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
