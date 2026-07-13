import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "doctrine" / "tools" / "summarize_harbor_trials.py"


class SummarizeHarborTrialsTests(unittest.TestCase):
    def write_trial(
        self,
        root: Path,
        *,
        commands: list[str],
        observations: list[str],
        skills: list[str] | None = None,
        lock_skills: list[dict[str, str]] | None = None,
        ledger_checked: bool = False,
        decision_written: bool = False,
        world: dict | None = None,
    ) -> Path:
        trial = root / "job" / "checkout-retries-m1__trial"
        (trial / "agent").mkdir(parents=True)
        (trial / "verifier").mkdir()
        trajectory = {
            "schema_version": "ATIF-v1.7",
            "steps": [
                {
                    "step_id": 1,
                    "source": "user",
                    "message": (
                        "<available_skills><skill><location>"
                        "/harbor/skills/doctrine/SKILL.md"
                        "</location></skill></available_skills>"
                    ),
                },
                {
                    "step_id": 2,
                    "source": "agent",
                    "tool_calls": [
                        {
                            "function_name": "bash_command",
                            "arguments": {"keystrokes": command},
                        }
                        for command in commands
                    ],
                    "observation": {
                        "results": [{"content": text} for text in observations]
                    },
                },
            ],
        }
        (trial / "agent" / "trajectory.json").write_text(
            json.dumps(trajectory), encoding="utf-8"
        )
        (trial / "result.json").write_text(
            json.dumps(
                {
                    "task_name": "books-doctrine/checkout-retries-m1",
                    "trial_name": "checkout-retries-m1__trial",
                    "config": {"agent": {"skills": skills or []}},
                    "agent_info": {
                        "name": "terminus-2",
                        "model_info": {"name": "qwen-test"},
                    },
                    "verifier_result": {"rewards": {"reward": 0.2}},
                    "exception_info": None,
                }
            ),
            encoding="utf-8",
        )
        realized_skills = lock_skills
        if realized_skills is None:
            realized_skills = [
                {
                    "name": Path(skill).name,
                    "source": skill,
                    "digest": "sha256:fixture",
                }
                for skill in (skills or [])
            ]
        (trial / "lock.json").write_text(
            json.dumps({"skills": realized_skills}), encoding="utf-8"
        )
        (trial / "verifier" / "detail.json").write_text(
            json.dumps(
                {
                    "ledger_check_during_agent_phase": ledger_checked,
                    "decision_md_present": decision_written,
                    "reward": 0.2,
                    **({"world": world} if world is not None else {}),
                }
            ),
            encoding="utf-8",
        )
        return trial

    def run_summary(self, root: Path) -> dict[str, object]:
        process = subprocess.run(
            [sys.executable, str(SCRIPT), str(root)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        return json.loads(process.stdout)

    def test_prompt_metadata_and_printed_examples_are_not_executed_events(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_trial(
                root,
                commands=["cat /app/docs/gateway-api.md\n"],
                observations=[
                    "python3 doctrine/tools/assemble_packet.py --render markdown"
                ],
                skills=["/home/halbritt/.agents/skills/doctrine"],
            )

            summary = self.run_summary(root)

        self.assertEqual("harbor-trial-stage-summary/1", summary["schema_version"])
        self.assertEqual(1, summary["trial_count"])
        self.assertEqual(1, summary["stage_counts"]["skill_injected"])
        self.assertEqual(0, summary["stage_counts"]["skill_read_invoked"])
        self.assertEqual(0, summary["stage_counts"]["packet_assembly_invoked"])
        stages = summary["trials"][0]["stages"]
        self.assertTrue(stages["skill_injected"])
        self.assertFalse(stages["skill_read_invoked"])
        self.assertFalse(stages["packet_assembly_invoked"])
        self.assertTrue(stages["gateway_docs_read_invoked"])

    def test_skill_injection_requires_a_realized_lock_entry(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_trial(
                root,
                commands=[],
                observations=[],
                skills=["/home/halbritt/.agents/skills/doctrine"],
                lock_skills=[],
            )

            summary = self.run_summary(root)

        self.assertFalse(summary["trials"][0]["stages"]["skill_injected"])

    def test_writing_evidence_shaped_text_is_not_evidence_reassembly(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_trial(
                root,
                commands=[
                    (
                        "cat > /tmp/observed.json <<'EOF'\n"
                        '{"schema_version":"evidence-record/1"}\nEOF\n'
                    )
                ],
                observations=[],
            )

            summary = self.run_summary(root)

        stages = summary["trials"][0]["stages"]
        self.assertFalse(stages["evidence_reassembly_invoked"])

    def test_commands_embedded_in_a_heredoc_are_not_executed_events(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_trial(
                root,
                commands=[
                    (
                        "cat > /tmp/note <<'EOF'\n"
                        "cat /harbor/skills/doctrine/SKILL.md\n"
                        "python3 doctrine/tools/assemble_packet.py --render markdown\n"
                        "EOF\n"
                    )
                ],
                observations=[],
                skills=["/home/halbritt/.agents/skills/doctrine"],
            )

            summary = self.run_summary(root)

        stages = summary["trials"][0]["stages"]
        self.assertFalse(stages["skill_read_invoked"])
        self.assertFalse(stages["packet_assembly_invoked"])

    def test_unsupported_trajectory_version_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            trial = self.write_trial(root, commands=[], observations=[])
            trajectory_path = trial / "agent" / "trajectory.json"
            trajectory = json.loads(trajectory_path.read_text(encoding="utf-8"))
            trajectory["schema_version"] = "ATIF-v99"
            trajectory_path.write_text(json.dumps(trajectory), encoding="utf-8")

            process = subprocess.run(
                [sys.executable, str(SCRIPT), str(root)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertNotEqual(0, process.returncode)
        self.assertIn("unsupported trajectory schema", process.stderr)

    def test_unsupported_agent_adapter_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            trial = self.write_trial(root, commands=[], observations=[])
            result_path = trial / "result.json"
            trial_result = json.loads(result_path.read_text(encoding="utf-8"))
            trial_result["agent_info"]["name"] = "codex"
            result_path.write_text(json.dumps(trial_result), encoding="utf-8")

            process = subprocess.run(
                [sys.executable, str(SCRIPT), str(root)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertNotEqual(0, process.returncode)
        self.assertIn("unsupported agent adapter", process.stderr)

    def test_executed_commands_and_verifier_detail_advance_stages(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_trial(
                root,
                commands=[
                    "cat /harbor/skills/verification-compact/SKILL.md\n",
                    "PYTHONDONTWRITEBYTECODE=1 make doctrine-check\n",
                    (
                        "python3 doctrine/tools/assemble_packet.py --evidence "
                        "/tmp/observed.json --render markdown\n"
                    ),
                    (
                        "cat > /tmp/observed.json <<'EOF'\n"
                        '{"schema_version":"evidence-record/1"}\nEOF\n'
                    ),
                    "cat /app/cmd/gateway/main.go\n",
                ],
                observations=[],
                skills=["/tmp/verification-compact"],
                ledger_checked=True,
                decision_written=True,
            )

            summary = self.run_summary(root)

        trial = summary["trials"][0]
        self.assertEqual("qwen-test", trial["model_name"])
        self.assertEqual(0.2, trial["reward"])
        self.assertFalse(trial["agent_error"])
        trajectory_artifact = trial["artifacts"]["agent/trajectory.json"]
        self.assertEqual(64, len(trajectory_artifact["sha256"]))
        stages = trial["stages"]
        self.assertTrue(stages["skill_read_invoked"])
        self.assertTrue(stages["corpus_gate_invoked"])
        self.assertTrue(stages["packet_assembly_invoked"])
        self.assertTrue(stages["evidence_reassembly_invoked"])
        self.assertTrue(stages["gateway_source_read_invoked"])
        self.assertTrue(stages["ledger_check_observed"])
        self.assertTrue(stages["substantial_decision_observed"])


if __name__ == "__main__":
    unittest.main()


class WorldStageTests(SummarizeHarborTrialsTests):
    def test_world_stages_advance_only_from_the_verifier_world_record(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_trial(
                root,
                commands=["echo replay_probe_observed payment_client_modified\n"],
                observations=["gateway_source_modified: true"],
                world={
                    "replay_probe_observed": True,
                    "payment_client_modified": False,
                    "gateway_source_modified": False,
                },
            )
            summary = self.run_summary(root)
        stages = summary["trials"][0]["stages"]
        self.assertTrue(stages["replay_probe_observed"])
        self.assertFalse(stages["payment_client_modified"])
        self.assertFalse(stages["gateway_source_modified"])
        self.assertEqual(1, summary["stage_counts"]["replay_probe_observed"])

    def test_missing_world_record_yields_false_world_stages(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_trial(root, commands=[], observations=[])
            summary = self.run_summary(root)
        stages = summary["trials"][0]["stages"]
        self.assertFalse(stages["replay_probe_observed"])
        self.assertFalse(stages["payment_client_modified"])
        self.assertFalse(stages["gateway_source_modified"])
