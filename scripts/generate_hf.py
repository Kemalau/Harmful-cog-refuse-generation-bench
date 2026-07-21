#!/usr/bin/env python3
"""Generate model responses for any of the three benchmark tasks."""

from __future__ import annotations

import argparse
import random

from io_utils import read_jsonl, write_jsonl


DEFAULT_DATA = {
    "recognition": "harmful_recognition/data.jsonl",
    "refusal": "refusal/data.jsonl",
    "generation": "harmful_generation/data.jsonl",
}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", choices=DEFAULT_DATA, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--data")
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-new-tokens", type=int)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--trust-remote-code", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    import torch
    from hf_utils import generate_text, load_model, render_chat

    random.seed(args.seed)
    torch.manual_seed(args.seed)
    data_path = args.data or DEFAULT_DATA[args.task]
    max_new_tokens = args.max_new_tokens or (16 if args.task == "recognition" else 512)
    rows = read_jsonl(data_path)
    model, tokenizer = load_model(args.model, args.trust_remote_code)
    results = []
    for index, row in enumerate(rows, start=1):
        user_text = row["evaluation_prompt"] if args.task == "recognition" else row["prompt"]
        if args.task == "generation":
            messages = [
                {"role": "user", "content": user_text},
                {"role": "assistant", "content": row["assistant_prefill"]},
            ]
            rendered = render_chat(tokenizer, messages, continue_final_message=True)
        else:
            rendered = render_chat(tokenizer, [{"role": "user", "content": user_text}])
        response = generate_text(
            model, tokenizer, rendered, max_new_tokens, args.temperature, args.top_p
        )
        result = dict(row)
        result.update(
            response=response,
            full_response=(row.get("assistant_prefill", "") + response),
            model=args.model,
            generation_config={
                "max_new_tokens": max_new_tokens,
                "temperature": args.temperature,
                "top_p": args.top_p,
                "seed": args.seed,
            },
        )
        results.append(result)
        if index % 25 == 0 or index == len(rows):
            print(f"generated {index}/{len(rows)}")
            write_jsonl(args.output, results)


if __name__ == "__main__":
    main()
