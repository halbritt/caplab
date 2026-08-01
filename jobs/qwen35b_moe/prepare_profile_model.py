"""Populate one persistent Hugging Face snapshot for a training profile."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .contract import ContractError
from .profile import load_training_profile


def run(config: Path, destination: Path) -> dict[str, str]:
    try:
        from huggingface_hub import snapshot_download
    except ImportError as error:
        raise ContractError("huggingface-hub is required for model preparation") from error
    profile = load_training_profile(config)
    destination = destination.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    snapshot_download(
        repo_id=profile.model_id,
        revision=profile.model_revision,
        local_dir=destination,
    )
    (destination / "snapshot-revision.txt").write_text(profile.model_revision + "\n")
    receipt = {
        "model_id": profile.model_id,
        "revision": profile.model_revision,
        "destination": str(destination),
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    run(args.config, args.destination)


if __name__ == "__main__":
    main()
