from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEPLOY = ROOT / "deploy" / "local-qwen-ft"


def test_llama_service_and_striatum_backend_share_tuned_alias():
    declaration = yaml.safe_load((DEPLOY / "backend.yaml").read_text())
    override = (DEPLOY / "llama-27b.override.conf").read_text()

    command = declaration["adapter"]["command"]
    model = command[command.index("-model") + 1]

    assert model == "qwen3.6-ft"
    assert "--alias qwen3.6-ft" in override
    assert "--lora /home/halbritt/models/Qwen3.6-35B-A3B-Striatum-FT/adapter-f32.gguf" in override
    assert "-m /home/halbritt/models/Qwen3.6-35B-A3B-APEX-I-Compact.gguf" in override
    assert "--port 8081" in override
