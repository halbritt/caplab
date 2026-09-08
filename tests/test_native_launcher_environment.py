"""Outer launcher policy, without any native harness or credential access."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from caplab.preference import native_live as preference
from caplab.review_dissent import native_live as review


ALLOWED = {"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"}
POISON = {
    "OPENROUTER_API_KEY": "synthetic-not-a-key",
    "STRIATUM_MCP_TOKEN": "synthetic-not-a-token",
    "FOAM_API": "synthetic-not-a-route",
    "ANTHROPIC_MODEL": "synthetic-unselected-model",
    "HTTP_PROXY": "http://invalid.example",
    "PYTHONPATH": "/caplab-fixture-does-not-exist",
    "BASH_ENV": "/caplab-fixture-does-not-exist",
    "CAPLAB_UNENUMERATED_OVERRIDE": "synthetic-value",
}


class NativeLauncherEnvironmentTest(unittest.TestCase):
    def test_preflight_scrubs_all_five_outer_processes(self):
        replies = [
            subprocess.CompletedProcess([], 0, b"fixture-claude\n", b""),
            subprocess.CompletedProcess([], 0, b"fixture-codex\n", b""),
            subprocess.CompletedProcess([], 0, b"fixture-bwrap\n", b""),
            subprocess.CompletedProcess([], 0, json.dumps({
                "loggedIn": True, "authMethod": "claude.ai",
                "apiProvider": "firstParty", "subscriptionType": "max",
            }).encode(), b""),
            subprocess.CompletedProcess([], 0, b"", b"Logged in using ChatGPT\n"),
        ]
        manifest = {"_instrument": {}, "runtime_versions": {
            "claude-code": "fixture-claude", "codex": "fixture-codex",
            "bubblewrap": "fixture-bwrap",
        }}
        with mock.patch.dict(os.environ, POISON, clear=True), \
                mock.patch.object(preference, "build_contained_version_probe",
                                  return_value={"command": ["/usr/bin/bwrap", "fixture"]}), \
                mock.patch.object(preference, "_contained_command",
                                  return_value=["/usr/bin/bwrap", "fixture"]), \
                mock.patch.object(preference.subprocess, "run", side_effect=replies) as run:
            observed = preference.preflight_native_runtime(manifest)
        self.assertEqual(observed["codex-auth"], "ChatGPT")
        self.assertEqual(run.call_count, 5)
        for call in run.call_args_list:
            self.assertEqual(call.kwargs.get("env"), ALLOWED)
        environments = [call.kwargs["env"] for call in run.call_args_list]
        self.assertEqual(len({id(env) for env in environments}), 5)

    def test_trial_processes_receive_only_explicit_environment(self):
        real_run = subprocess.run
        for module, execute, prepare, record in (
                (preference, "execute_native_trial", "prepare_native_trial",
                 "record_native_observation"),
                (review, "execute_native_review_trial", "prepare_native_review_trial",
                 "record_native_review_observation")):
            with self.subTest(module=module.__name__), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / "input/task").mkdir(parents=True)
                (root / "launch.json").write_text(json.dumps({"launch_sha256": "fixture"}))
                manifest = {
                    "campaign_id": "synthetic-env-probe", "manifest_sha256": "fixture",
                    "_instrument": {"execution_order": ["task:subject"],
                                    "cells": {"task": {"public_task_id": "task"}}},
                    "limits": {"trial_wall_clock_minutes": 1},
                }

                def probe(command, **kwargs):
                    self.assertEqual(command, ["/usr/bin/bwrap", "fixture"])
                    # Replace only the launcher executable. The real child sees
                    # exactly the environment passed by the production caller.
                    return real_run([sys.executable, "-S", "-c",
                                     "import os,json;print(json.dumps(dict(os.environ)))"],
                                    **kwargs)

                with mock.patch.dict(os.environ, POISON, clear=True), \
                        mock.patch.object(module, "preflight_native_runtime", return_value={}), \
                        mock.patch.object(module, prepare,
                                          return_value=(root, ["/usr/bin/bwrap", "fixture"])), \
                        mock.patch.object(module, record), \
                        mock.patch.object(module.subprocess, "run", side_effect=probe):
                    result = getattr(module, execute)(manifest, slot_index=0,
                                                       attempt_kind="primary", prior_attempts=[])
                self.assertEqual(result, root)
                observed = json.loads((root / "native.stdout").read_bytes())
                self.assertEqual(observed, ALLOWED)
                completion = json.loads((root / "completion.json").read_bytes())
                self.assertEqual(completion["return_code"], 0)
                self.assertFalse(completion["timed_out"])


if __name__ == "__main__":
    unittest.main()
