import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "doctrine" / "tools"))

from run_checkout_activation import (  # noqa: E402
    ENDPOINT_TOKEN,
    MODEL_TOKEN,
    Trial,
    load_order,
    selected_trials,
    trial_command,
)


def _option(command, name):
    return command[command.index(name) + 1]


def test_preregistered_order_has_48_contiguous_trials():
    order = load_order()

    assert len(order) == 48
    assert [trial.sequence for trial in order] == list(range(1, 49))


def test_bare_27b_command_uses_exact_route_and_sampling():
    trial = Trial(2, 1, "27b", "m1", "bare")
    command = trial_command(trial, Path("/tmp/jobs"))

    assert _option(command, "--model") == "qwen3.6:27b"
    assert _option(command, "--max-context") == "32768"
    assert f"openai/{MODEL_TOKEN}" in command
    assert f"api_base={ENDPOINT_TOKEN}" in command
    assert "temperature=0.6" in command
    assert 'llm_kwargs={"top_p":0.95,"presence_penalty":0,"max_tokens":8192}' in command
    assert 'llm_call_kwargs={"extra_body":{"top_k":20,"min_p":0}}' in command
    assert "--skill" not in command
    assert "--extra-instruction-path" not in command
    assert _option(command, "--n-concurrent") == "1"
    assert _option(command, "--max-retries") == "0"


def test_forced_35b_command_injects_compact_skill_and_instruction():
    command = trial_command(Trial(1, 1, "35b", "m1", "forced"), Path("/tmp/jobs"))

    assert _option(command, "--model") == "qwen3.6-35b-a3b"
    assert _option(command, "--max-context") == "262144"
    assert _option(command, "--skill").endswith("experimental-skills/verification-compact/doctrine")
    assert _option(command, "--extra-instruction-path").endswith(
        "conditions/verification-compact-forced.md"
    )


def test_resume_selection_preserves_recorded_order():
    selected = selected_trials(load_order(), first=47, limit=None)

    assert [trial.sequence for trial in selected] == [47, 48]
