#!/usr/bin/env python3
"""Regenerate hashes for repository benchmark artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    "harmful_recognition/data.jsonl",
    "harmful_recognition/base_prompts.jsonl",
    "refusal/data.jsonl",
    "refusal/judge_prompt.txt",
    "harmful_generation/data.jsonl",
    "harmful_generation/judge_prompt.txt",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def line_count(path: Path) -> int | None:
    if path.suffix != ".jsonl":
        return None
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


manifest = {
    "benchmark_version": "1.3.0",
    "sampling_seed": 20260721,
    "model_inputs": 500,
    "unique_base_prompts": 300,
    "files": {
        name: {"records": line_count(ROOT / name), "sha256": sha256(ROOT / name)}
        for name in FILES
    },
    "upstream_sources": {
        "AdvBench": "https://github.com/llm-attacks/llm-attacks",
        "HarmBench": "https://github.com/centerforaisafety/HarmBench",
        "BeaverTails": "https://huggingface.co/datasets/PKU-Alignment/BeaverTails",
        "Stanford Alpaca": "https://github.com/tatsu-lab/stanford_alpaca",
    },
}
(ROOT / "manifest.json").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print("updated manifest.json")
