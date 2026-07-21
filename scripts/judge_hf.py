#!/usr/bin/env python3
"""Run a Hugging Face LLM judge over refusal or generation responses."""

from __future__ import annotations

import argparse
from pathlib import Path

from io_utils import extract_json, read_jsonl, write_jsonl


DEFAULT_TEMPLATE = {
    "refusal": "refusal/judge_prompt.txt",
    "generation": "harmful_generation/judge_prompt.txt",
}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", choices=DEFAULT_TEMPLATE, required=True)
    parser.add_argument("--responses", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--template")
    parser.add_argument("--max-new-tokens", type=int, default=384)
    parser.add_argument("--trust-remote-code", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    from hf_utils import generate_text, load_model, render_chat

    template = Path(args.template or DEFAULT_TEMPLATE[args.task]).read_text(encoding="utf-8")
    rows = read_jsonl(args.responses)
    model, tokenizer = load_model(args.model, args.trust_remote_code)
    if "[User Message]" in template:
        system_template, user_template = template.split("[User Message]", 1)
        system_template = system_template.replace("[System Prompt]", "", 1).strip()
        user_template = user_template.strip()
    else:
        system_template, user_template = "", template
    results = []
    for index, row in enumerate(rows, start=1):
        def fill(text):
            return (text.replace("{prompt}", row["prompt"])
            .replace("{assistant_prefill}", row.get("assistant_prefill", ""))
            .replace("{response}", row.get("response", "")))
        messages = []
        if system_template:
            messages.append({"role": "system", "content": fill(system_template)})
        messages.append({"role": "user", "content": fill(user_template)})
        rendered = render_chat(tokenizer, messages)
        raw = generate_text(model, tokenizer, rendered, args.max_new_tokens, 0.0, 1.0)
        result = dict(row)
        judgment = extract_json(raw)
        result.update(
            judge_model=args.model,
            judge_raw=raw,
            judgment=judgment,
            judge_parse_error=judgment is None,
        )
        results.append(result)
        if index % 25 == 0 or index == len(rows):
            print(f"judged {index}/{len(rows)}")
            write_jsonl(args.output, results)


if __name__ == "__main__":
    main()
