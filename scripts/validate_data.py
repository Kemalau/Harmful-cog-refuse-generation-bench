#!/usr/bin/env python3
"""Validate benchmark sizes, class balance, IDs, and cross-task overlap."""

from __future__ import annotations

import re
from collections import Counter
from itertools import product

from io_utils import read_jsonl


def norm(text):
    return " ".join(re.findall(r"[a-z0-9]+", text.lower()))


def jaccard(a, b):
    aa, bb = set(norm(a).split()), set(norm(b).split())
    return len(aa & bb) / len(aa | bb) if aa and bb else 0.0


recognition = read_jsonl("harmful_recognition/data.jsonl")
recognition_base = read_jsonl("harmful_recognition/base_prompts.jsonl")
refusal = read_jsonl("refusal/data.jsonl")
generation = read_jsonl("harmful_generation/data.jsonl")

assert (len(recognition), len(recognition_base), len(refusal), len(generation)) == (300, 100, 100, 100)
assert Counter(row["safety_label"] for row in recognition_base) == {"harmful": 50, "benign": 50}
assert Counter(row["safety_label"] for row in refusal) == {"harmful": 50, "benign": 50}
assert Counter(row["safety_label"] for row in generation) == {"harmful": 50, "benign": 50}
assert Counter(row["template_id"] for row in recognition) == {
    "harm_yes_no": 100, "safe_yes_no": 100, "safe_harmful_label": 100
}
assert len({row["id"] for row in recognition + refusal + generation}) == 500

groups = [recognition_base, refusal, generation]
for left, right in ((0, 1), (0, 2), (1, 2)):
    assert all(jaccard(a["prompt"], b["prompt"]) < 0.70 for a, b in product(groups[left], groups[right]))

print("OK: 500 inputs; balanced labels; no cross-task pair has token Jaccard >= 0.70")
