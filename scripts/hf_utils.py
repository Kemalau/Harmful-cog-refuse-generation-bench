#!/usr/bin/env python3
"""Hugging Face model loading and deterministic text generation."""

from __future__ import annotations

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def load_model(model_name: str, trust_remote_code: bool = False):
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=trust_remote_code)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        torch_dtype="auto",
        trust_remote_code=trust_remote_code,
    )
    model.eval()
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id
    return model, tokenizer


def render_chat(tokenizer, messages: list[dict], continue_final_message: bool = False) -> str:
    kwargs = {
        "tokenize": False,
        "add_generation_prompt": not continue_final_message,
        "continue_final_message": continue_final_message,
        "enable_thinking": False,
    }
    try:
        return tokenizer.apply_chat_template(messages, **kwargs)
    except TypeError:
        kwargs.pop("enable_thinking", None)
        try:
            return tokenizer.apply_chat_template(messages, **kwargs)
        except TypeError:
            kwargs.pop("continue_final_message", None)
            if continue_final_message:
                prefill = messages[-1]["content"]
                return tokenizer.apply_chat_template(
                    messages[:-1], tokenize=False, add_generation_prompt=True
                ) + prefill
            return tokenizer.apply_chat_template(messages, **kwargs)


@torch.inference_mode()
def generate_texts(
    model,
    tokenizer,
    rendered_prompts: list[str],
    max_new_tokens: int,
    temperature: float,
    top_p: float,
) -> list[str]:
    tokenizer.padding_side = "left"
    inputs = tokenizer(rendered_prompts, return_tensors="pt", padding=True)
    device = model.get_input_embeddings().weight.device
    inputs = {key: value.to(device) for key, value in inputs.items()}
    kwargs = {
        "max_new_tokens": max_new_tokens,
        "pad_token_id": tokenizer.pad_token_id,
        "eos_token_id": tokenizer.eos_token_id,
        "do_sample": temperature > 0,
    }
    if temperature > 0:
        kwargs.update(temperature=temperature, top_p=top_p)
    output = model.generate(**inputs, **kwargs)
    continuations = output[:, inputs["input_ids"].shape[1]:]
    return [text.strip() for text in tokenizer.batch_decode(continuations, skip_special_tokens=True)]


def generate_text(
    model,
    tokenizer,
    rendered_prompt: str,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
) -> str:
    return generate_texts(
        model, tokenizer, [rendered_prompt], max_new_tokens, temperature, top_p
    )[0]
