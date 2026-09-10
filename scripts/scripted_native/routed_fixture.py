"""Own the scripted endpoint outside the routed workload and its cgroup."""

import asyncio
from concurrent.futures import Future
from contextlib import contextmanager
from types import SimpleNamespace
import os
import threading
import time

from .fixture import Fixture
from .payload import scripted_response


@contextmanager
def supervised_fixture(
    *,
    expected_identity,
    capture_dir,
    observation_socket,
    quarantine_factory,
    bind_address="198.18.0.1",
):
    """Yield a ready endpoint; retain its summary only after joining its owner.

    Caller owns the disconnected network, native body deadline and authenticated
    observation listener. Socket handshakes have their own five-second timeout.
    Startup/worker failures propagate; cleanup does not hide a body exception.
    """
    stop = threading.Event()
    started, finished = Future(), Future()
    result = SimpleNamespace(summary=None)

    async def serve():
        async with Fixture(
            scripted_response,
            expected_identity=expected_identity,
            capture_dir=capture_dir,
            observation_socket=observation_socket,
            bind_address=bind_address,
            quarantine_factory=quarantine_factory,
        ) as fixture:
            result.uri = fixture.uri
            result.port = fixture.server.sockets[0].getsockname()[1]
            result.peer_pid = os.getpid()
            started.set_result(None)
            while not stop.is_set():
                await asyncio.sleep(0.025)
        result.summary = {
            "schema": "caplab.supervised-scripted-fixture/v1",
            "bind_address": bind_address,
            "port": result.port,
            "peer_pid": result.peer_pid,
            "requests": fixture.http_requests,
            "errors": fixture.errors,
            "scripted_generated_responses": fixture.generated,
            "websocket_messages": fixture.messages,
            "library_events": fixture.library_events,
            "deferred_close": fixture.deferred_close,
            "fixture_stop_reason": "fixture_error" if fixture.stop_required else None,
            "fixture_closed": fixture.closed,
            "study_eligible": False,
        }

    def worker():
        try:
            asyncio.run(serve())
        except BaseException as error:
            if not started.done():
                started.set_exception(error)
            finished.set_exception(error)
        else:
            finished.set_result(None)

    thread = threading.Thread(target=worker, name="caplab-scripted-fixture")
    thread.start()
    try:
        started.result(timeout=5)
        yield result
    finally:
        stop.set()
        thread.join(timeout=8)
        if thread.is_alive():
            raise TimeoutError("scripted fixture thread did not stop")
        finished.result()
        result.summary["fixture_thread_joined"] = True
        result.summary["finished_monotonic_ns"] = time.monotonic_ns()
