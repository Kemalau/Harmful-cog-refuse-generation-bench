# Harmful Generation

`data.jsonl` contains 100 prompts: 25 BeaverTails harmful, 25 HarmBench harmful, and 50 procedural Alpaca benign. Every record includes one of four balanced `assistant_prefill` strings.

The model must continue the assistant turn after the prefill. `judge_prompt.txt` assigns anchored 1–5 scores for harmful actionable generation, linguistic coherence, and prompt relevance.

Run:

```bash
python scripts/generate_hf.py --task generation --model MODEL --output results/generation.jsonl
python scripts/judge_hf.py --task generation --responses results/generation.jsonl --model JUDGE --output results/generation_judged.jsonl
python scripts/score_generation.py --judged-responses results/generation_judged.jsonl --output results/generation_metrics.json
```
