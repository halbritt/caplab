#!/usr/bin/env python3
"""Transient OpenAI-compatible base/tuned server for CAPLAB-16 evaluation."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", type=Path, required=True)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--adapter-dir", type=Path, required=True)
    parser.add_argument("--bind", required=True)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--ready-file", type=Path, required=True)
    args = parser.parse_args()

    import torch
    from peft import PeftModel
    from transformers import AutoModelForImageTextToText, AutoTokenizer, BitsAndBytesConfig

    experiment = json.loads(args.experiment.read_text(encoding="utf-8"))
    if sha256_file(args.model_dir / "model.safetensors.index.json") != experiment["base_checkpoint"]["index_sha256"]:
        raise RuntimeError("checkpoint_index_sha256_mismatch")
    if not (args.adapter_dir / "adapter_model.safetensors").is_file():
        raise RuntimeError("sealed_adapter_missing")
    tokenizer = AutoTokenizer.from_pretrained(args.model_dir, local_files_only=True)
    quantization = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
    )
    base = AutoModelForImageTextToText.from_pretrained(
        args.model_dir,
        local_files_only=True,
        quantization_config=quantization,
        torch_dtype=torch.bfloat16,
        device_map={"": 0},
        low_cpu_mem_usage=True,
    )
    model = PeftModel.from_pretrained(base, args.adapter_dir, is_trainable=False)
    model.eval()
    lock = threading.Lock()
    model_ids = {
        "caplab-qwen3.6-27b-base": False,
        "caplab-qwen3.6-27b-tuned": True,
    }

    class Handler(BaseHTTPRequestHandler):
        server_version = "caplab-qwen27b-eval/1"

        def log_message(self, format: str, *values: object) -> None:
            print(format % values, flush=True)

        def send_json(self, status: int, value: object) -> None:
            body = canonical(value)
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            if self.path == "/health":
                self.send_json(HTTPStatus.OK, {"status": "ok"})
            elif self.path == "/v1/models":
                self.send_json(HTTPStatus.OK, {
                    "object": "list",
                    "data": [{"id": item, "object": "model"} for item in model_ids],
                })
            else:
                self.send_json(HTTPStatus.NOT_FOUND, {"error": {"message": "not found"}})

        def do_POST(self) -> None:
            if self.path != "/v1/chat/completions":
                self.send_json(HTTPStatus.NOT_FOUND, {"error": {"message": "not found"}})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                request = json.loads(self.rfile.read(length))
                model_id = request["model"]
                messages = request["messages"]
                max_tokens = int(request.get("max_tokens", 4096))
                temperature = float(request.get("temperature", 0))
                if model_id not in model_ids or temperature != 0 or not (1 <= max_tokens <= 4096):
                    raise ValueError("frozen_request_contract_mismatch")
                if not isinstance(messages, list) or not messages:
                    raise ValueError("messages_required")
                prompt = tokenizer.apply_chat_template(
                    messages, tokenize=False, add_generation_prompt=True
                )
                encoded = tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
                encoded = {key: value.to("cuda:0") for key, value in encoded.items()}
                adapter_context = contextlib.nullcontext() if model_ids[model_id] else model.disable_adapter()
                with lock, adapter_context, torch.inference_mode():
                    generated = model.generate(
                        **encoded,
                        max_new_tokens=max_tokens,
                        do_sample=False,
                        use_cache=True,
                        pad_token_id=tokenizer.eos_token_id,
                    )
                output_ids = generated[0, encoded["input_ids"].shape[1]:]
                content = tokenizer.decode(output_ids, skip_special_tokens=True).strip()
                if not content:
                    raise ValueError("empty_model_content")
                self.send_json(HTTPStatus.OK, {
                    "id": "caplab-eval",
                    "object": "chat.completion",
                    "model": model_id,
                    "choices": [{
                        "index": 0,
                        "finish_reason": "stop",
                        "message": {"role": "assistant", "content": content},
                    }],
                    "usage": {
                        "prompt_tokens": encoded["input_ids"].shape[1],
                        "completion_tokens": len(output_ids),
                        "total_tokens": encoded["input_ids"].shape[1] + len(output_ids),
                    },
                })
            except Exception as error:
                self.send_json(HTTPStatus.BAD_REQUEST, {
                    "error": {"message": f"{type(error).__name__}: {error}"}
                })

    ready = {
        "schema": "caplab.training.eval-server-ready/v1",
        "bind": args.bind,
        "port": args.port,
        "models": list(model_ids),
        "adapter_sha256": sha256_file(args.adapter_dir / "adapter_model.safetensors"),
    }
    args.ready_file.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(args.ready_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(canonical(ready) + b"\n")
        stream.flush()
        os.fsync(stream.fileno())
    ThreadingHTTPServer((args.bind, args.port), Handler).serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
