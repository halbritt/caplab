"""Private fixed protocol fixture; no model inference or native execution."""

import asyncio
import hashlib
import json
import logging
import re
import socket
import time
from websockets.asyncio.server import serve, ServerConnection
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

# The supervisor imports a package; the capsule mounts these files individually.
if __package__:
    from .payload import identity_expectation, request_identity
else:
    from payload import identity_expectation, request_identity

MAX_MESSAGE = 1048576


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def invalid_constant(value):
    raise ValueError("nonfinite JSON constant")


class HTTPConnection(ServerConnection):
    def __init__(self, *args, fixture, **kwargs):
        super().__init__(*args, **kwargs)
        self.fixture = fixture
        self.prefix = bytearray()
        self.route = None
        self.ancillary_done = False

    def data_received(self, data):
        if self.route == "websocket":
            return super().data_received(data)
        if self.ancillary_done:
            return
        if len(self.prefix) + len(data) > MAX_MESSAGE + 16384:
            return self.reject("HTTP byte limit")
        self.prefix.extend(data)
        if self.route is None:
            if len(self.prefix) < 5:
                return
            if not self.prefix.startswith(b"POST "):
                self.route = "websocket"
                raw = bytes(self.prefix)
                self.prefix.clear()
                return super().data_received(raw)
            self.route = "post"
        end = self.prefix.find(b"\r\n\r\n")
        if end < 0:
            if len(self.prefix) > 16384:
                self.reject("HTTP header limit")
            return
        try:
            if end + 4 > 16384:
                raise ValueError("HTTP header limit")
            lines = bytes(self.prefix[:end]).decode("ascii").split("\r\n")
            method, path, version = lines[0].split(" ")
            if (
                method != "POST"
                or version != "HTTP/1.1"
                or not path.startswith("/")
                or len(path) > 256
            ):
                raise ValueError("invalid HTTP request line")
            fields = []
            for line in lines[1:]:
                key, value = line.split(":", 1)
                if not key or key.strip() != key:
                    raise ValueError("invalid HTTP header")
                fields.append((key.lower(), value.strip()))
            lengths = [value for key, value in fields if key == "content-length"]
            if len(lengths) != 1 or not re.fullmatch("[0-9]{1,7}", lengths[0]):
                raise ValueError("invalid HTTP content length")
            if any(key == "transfer-encoding" for key, value in fields):
                raise ValueError("HTTP transfer encoding unsupported")
            length = int(lengths[0])
            if length > MAX_MESSAGE:
                raise ValueError("HTTP body limit")
            body = bytes(self.prefix[end + 4 :])
            if len(body) < length:
                return
            if len(body) != length:
                raise ValueError("extra HTTP body bytes")
            entry = {
                "method": "POST",
                "path": path,
                "body_bytes": length,
                "body_sha256": hashlib.sha256(body).hexdigest(),
                "status": 405 if path == "/responses" else 404,
                "received_monotonic_ns": time.monotonic_ns(),
            }
            if len(self.fixture.http_requests) >= 32:
                raise ValueError("HTTP request limit")
            self.fixture.http_requests.append(entry)
            if path == "/responses":
                self.fixture.errors.append("unexpected HTTP response fallback")
            self.respond_http(entry["status"])
        except (ValueError, UnicodeError) as error:
            self.reject(str(error))

    def reject(self, reason):
        self.fixture.errors.append(reason)
        self.respond_http(400)

    def respond_http(self, status):
        self.ancillary_done = True
        self.prefix.clear()
        labels = {400: "Bad Request", 404: "Not Found", 405: "Method Not Allowed"}
        body = b'{"error":"synthetic unsupported request"}'
        raw = (
            f"HTTP/1.1 {status} {labels[status]}\r\nContent-Type: application/json\r\nContent-Length: {len(body)}\r\nConnection: close\r\n\r\n"
        ).encode() + body
        self.transport.write(raw)
        self.transport.close()

    def connection_lost(self, exc):
        if self.route == "post" and not self.ancillary_done:
            self.fixture.errors.append("incomplete HTTP POST")
        super().connection_lost(exc)


class FixtureLog(logging.Handler):
    def __init__(self, fixture):
        super().__init__(level=logging.WARNING)
        self.fixture = fixture

    def emit(self, record):
        f = self.fixture
        if len(f.library_events) >= 32:
            if "library event limit" not in f.errors:
                f.errors.append("library event limit")
            f.server.close()
            return
        expected = getattr(getattr(record, "websocket", None), "ancillary_done", False)
        entry = {
            "classification": "handled-http-post"
            if expected
            else "unexpected-library-error",
            "level": record.levelname,
            "message": record.getMessage()[:256],
        }
        f.library_events.append(entry)
        if not expected:
            f.errors.append("unexpected library error")


class Fixture:
    def __init__(
        self,
        response_builder,
        *,
        expected_identity,
        deadline_seconds=30,
        capture_dir=None,
        observation_socket=None,
        bind_address="127.0.0.1",
        quarantine_factory=None,
    ):
        if type(deadline_seconds) not in (int, float) or not 0 < deadline_seconds <= 30:
            raise ValueError("invalid deadline")
        if bind_address not in ("127.0.0.1", "198.18.0.1"):
            raise ValueError("unsupported fixture bind address")
        self.bind_address = bind_address
        self.quarantine_factory = quarantine_factory
        self.observation_socket = observation_socket
        self.expected_identity = identity_expectation(expected_identity)
        self.response_builder = response_builder
        self.deadline_seconds = deadline_seconds
        self.generated = 0
        self.last_id = None
        self.warmup_input = None
        self.errors = []
        self.deferred_close = None
        self.messages = []
        self.done = asyncio.Event()
        self.closed = False
        self.http_requests = []
        self.admitted = False
        self.library_events = []
        self.capture_dir = capture_dir
        self.logger = logging.Logger("caplab.fixed.websocket")
        self.logger.addHandler(FixtureLog(self))

    @property
    def stop_required(self):
        if self.deferred_close is not None and self.errors == [
            self.deferred_close["error"]
        ]:
            return False
        return bool(self.errors)

    async def __aenter__(self):
        if self.capture_dir is not None:
            if self.quarantine_factory is not None:
                from caplab.capture_quarantine import check_capture_bytes
                import os

                check_capture_bytes(
                    self.quarantine_factory, os.fsencode(self.capture_dir)
                )
            self.capture_dir.mkdir(mode=0o700)
        self.server = await serve(
            self.handle,
            self.bind_address,
            0,
            compression=None,
            max_size=MAX_MESSAGE,
            max_queue=2,
            open_timeout=2,
            close_timeout=1,
            ping_interval=None,
            origins=[None],
            process_request=self.request,
            process_response=self.response,
            logger=self.logger,
            create_connection=lambda *a, **k: HTTPConnection(*a, fixture=self, **k),
        )
        self.uri = (
            "ws://"
            + self.bind_address
            + ":"
            + str(self.server.sockets[0].getsockname()[1])
            + "/responses"
        )
        return self

    def request(self, connection, request):
        if len(self.http_requests) >= 32:
            if "HTTP request limit" not in self.errors:
                self.errors.append("HTTP request limit")
            self.server.close()
            return connection.respond(429, "fixture request limit")
        entry = {
            "method": "GET",
            "path": request.path[:256],
            "received_monotonic_ns": time.monotonic_ns(),
        }
        self.http_requests.append(entry)
        if request.path == "/__fixture_check":
            entry["status"] = 200
            return connection.respond(200, '{"fixture":true}')
        if request.path != "/responses":
            entry["status"] = 404
            return connection.respond(404, "unsupported fixture request")
        if self.admitted:
            entry["status"] = 409
            self.errors.append("additional websocket refused")
            return connection.respond(409, "fixture connection already consumed")
        self.admitted = True
        entry["status"] = "handshake pending"
        return None

    def response(self, connection, request, response):
        for entry in reversed(self.http_requests):
            if entry["path"] == request.path and entry["status"] == "handshake pending":
                entry["status"] = response.status_code
                break
        return response

    def retain(self, name, raw):
        if len(raw) > MAX_MESSAGE:
            raise ValueError("retained fixture artifact too large")
        if self.capture_dir is not None:
            if self.quarantine_factory is not None:
                from caplab.capture_quarantine import check_capture_bytes
                import os

                check_capture_bytes(
                    self.quarantine_factory, os.fsencode(self.capture_dir / name)
                )
                check_capture_bytes(self.quarantine_factory, raw)
            with (self.capture_dir / name).open("xb") as out:
                out.write(raw)
        return {
            "path": name,
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
        }

    async def __aexit__(self, *args):
        self.server.close()
        await self.server.wait_closed()
        self.closed = True

    @staticmethod
    def decode_events(sse):
        return [
            json.loads(line[6:])
            for line in sse.splitlines()
            if line.startswith(b"data: ")
        ]

    async def handle(self, connection):
        try:
            async with asyncio.timeout(self.deadline_seconds) as deadline:
                while True:
                    raw = await connection.recv()
                    if not isinstance(raw, str):
                        raise ValueError("requires text frame")
                    encoded = raw.encode("utf-8")
                    if len(self.messages) >= 3:
                        raise ValueError("message limit")
                    if len(encoded) > MAX_MESSAGE:
                        raise ValueError("message byte limit")
                    number = len(self.messages)
                    request_artifact = self.retain(
                        str(number) + ".request.json", encoded
                    )
                    self.messages.append(
                        {
                            "request_artifact": request_artifact,
                            "bytes": len(encoded),
                            "sha256": hashlib.sha256(encoded).hexdigest(),
                            "received_monotonic_ns": time.monotonic_ns(),
                        }
                    )
                    document = json.loads(
                        raw,
                        object_pairs_hook=unique_object,
                        parse_constant=invalid_constant,
                    )
                    if (
                        not isinstance(document, dict)
                        or document.get("type") != "response.create"
                    ):
                        raise ValueError("requires response.create")
                    if (
                        "generate" in document
                        and type(document["generate"]) is not bool
                    ):
                        raise ValueError("invalid generate flag")
                    if (
                        not isinstance(document.get("input"), list)
                        or len(document["input"]) > 100
                    ):
                        raise ValueError("invalid input items")
                    if self.generated == 2:
                        raise ValueError("generated response limit")
                    if document.get("previous_response_id") != self.last_id:
                        raise ValueError("response lineage differs")
                    self.messages[-1]["request_identity"] = request_identity(
                        document, self.expected_identity
                    )
                    if number == 0 and self.observation_socket is not None:
                        timing = self.messages[-1]
                        timing["child_observation_requested_monotonic_ns"] = (
                            time.monotonic_ns()
                        )
                        with socket.socket(
                            socket.AF_UNIX, socket.SOCK_SEQPACKET
                        ) as channel:
                            channel.settimeout(5)
                            channel.connect(self.observation_socket)
                            channel.sendall(timing["sha256"].encode("ascii"))
                            ack, ancillary, flags, _ = channel.recvmsg(1)
                            if ancillary or flags or ack != b"1":
                                raise ValueError(
                                    "child observation acknowledgement differs"
                                )
                        timing["child_observation_acknowledged_monotonic_ns"] = (
                            time.monotonic_ns()
                        )
                        if asyncio.get_running_loop().time() >= deadline.when():
                            raise TimeoutError(
                                "fixture deadline elapsed during child observation"
                            )
                    if document.get("generate") is False:
                        if self.warmup_input is not None or self.generated:
                            raise ValueError("warmup out of order")
                        events = self.decode_events(self.response_builder(document, 1))
                        response = events[0]["response"] | {
                            "id": "resp_caplab_warmup",
                            "status": "completed",
                            "output": [],
                        }
                        events = [
                            {
                                "type": "response.created",
                                "sequence_number": 0,
                                "response": response | {"status": "in_progress"},
                            },
                            {
                                "type": "response.completed",
                                "sequence_number": 1,
                                "response": response,
                            },
                        ]
                        self.warmup_input = document["input"]
                    else:
                        effective = document
                        if self.generated == 0 and self.warmup_input is not None:
                            effective = document | {
                                "input": self.warmup_input + document["input"]
                            }
                        events = self.decode_events(
                            self.response_builder(effective, self.generated + 1)
                        )
                        self.generated += 1
                    self.last_id = events[-1]["response"]["id"]
                    sent = [json.dumps(event) for event in events]
                    self.messages[-1]["events_artifact"] = self.retain(
                        str(number) + ".events.jsonl", ("\n".join(sent) + "\n").encode()
                    )
                    for raw_event in sent:
                        await connection.send(raw_event)
                    self.messages[-1]["written_monotonic_ns"] = time.monotonic_ns()
        except ConnectionClosedOK:
            if self.generated != 2:
                self.errors.append("incomplete exchange")
        except ConnectionClosedError as error:
            detail = type(error).__name__ + ": " + str(error)[:256]
            if (
                not self.errors
                and error.rcvd is None
                and error.sent is None
                and self.generated == 2
                and self.messages
                and "written_monotonic_ns" in self.messages[-1]
            ):
                self.deferred_close = {
                    "error_index": 0,
                    "error": detail,
                    "generated_responses": 2,
                    "received_close_code": None,
                    "sent_close_code": None,
                    "observed_monotonic_ns": time.monotonic_ns(),
                }
            self.errors.append(detail)
            await connection.close(code=1008, reason="fixture refused exchange")
        except Exception as error:
            self.errors.append(type(error).__name__ + ": " + str(error)[:256])
            await connection.close(code=1008, reason="fixture refused exchange")
        finally:
            self.done.set()
