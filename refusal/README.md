# Refusal

`data.jsonl` contains 100 prompts: 25 AdvBench harmful, 25 HarmBench-standard harmful, and 50 Alpaca benign. HarmBench copyright/contextual rows are excluded. Generate normally without an assistant prefill.

`judge_prompt.txt` evaluates refusal, harmful actionable-information leakage, linguistic coherence, and prompt relevance. It is adapted from Appendix K.1 of arXiv:2605.08513.

Run:

```bash
python scripts/generate_hf.py --task refusal --model MODEL --output results/refusal.jsonl
python scripts/judge_hf.py --task refusal --responses results/refusal.jsonl --model JUDGE --output results/refusal_judged.jsonl
python scripts/score_refusal.py --judged-responses results/refusal_judged.jsonl --output results/refusal_metrics.json
```
