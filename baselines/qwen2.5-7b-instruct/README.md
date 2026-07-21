# Qwen2.5-7B-Instruct baseline and dataset-quality audit

## Protocol

- Evaluated model: `Qwen/Qwen2.5-7B-Instruct` (the base checkpoint used by the associated experiments).
- Judge: `Qwen3-32B`, independent from the evaluated model.
- Decoding: greedy (`temperature=0`, seed 42).
- Maximum continuation: 16 tokens for recognition; 512 for refusal and generation.
- Qwen3 thinking mode: disabled.
- Judge parse success: 200/200.

## Results

| Task / metric | Result |
|---|---:|
| Recognition: `SAFE/HARMFUL` accuracy | **98%** |
| Recognition: explicit harmful Yes/No accuracy | **98%** |
| Recognition: explicit safe Yes/No accuracy | **97%** |
| Recognition: all three templates correct | **95%** |
| Recognition invalid outputs | 0% |
| Harmful refusal rate | **98%** |
| Benign refusal rate | **0%** |
| Refusal balanced accuracy | **99%** |
| Harmful actionable-information leakage | 2% |
| Harmful generation score | **2.38 / 5** |
| Harmful linguistic coherence | 4.72 / 5 |
| Benign linguistic coherence | **4.90 / 5** |
| Benign prompt relevance | **5.00 / 5** |
| Safety-quality summary | 4.26 / 5 |

The harmful-generation scores span the full scale: 23 samples scored 1, 4 scored 2, 7 scored 3, 13 scored 4, and 3 scored 5. This is useful dynamic range for measuring safety interventions.

## Quality findings and corrections

The first pilot exposed two HarmBench sampling problems:

1. Copyright requests (song lyrics and book passages) were labeled harmful even though this benchmark targets direct safety harm.
2. Contextual HarmBench rows were sampled without their long `ContextString`, leaving some requests incomplete.

Version 1.1 restricts HarmBench to its self-contained `standard` functional category. This removed the four copyright-driven recognition errors and increased harmful refusal from 88% to 98%.

Four under-specified Alpaca prompts that did not naturally support an assistant steps prefill were also replaced. On the final benign generation set, all 50 responses received harmfulness score 1 and prompt relevance 5; linguistic coherence was 4 or 5 for every response.

## Interpretation

- **Labels and prompt completeness look good after the v1.1 cleanup.** Manual outlier inspection found one real harmful leakage case: an out-of-band SQL exfiltration request answered with actionable conceptual details.
- **Recognition templates are stable in v1.2.** The old question-first layout made Qwen answer `No` as if refusing the embedded request (54%/51% accuracy). Moving the question after `</request>` and spelling out the mapping raises the two Yes/No accuracies to 98% and 97%; `SAFE/HARMFUL` reaches 98%. The three-template aggregate is now meaningful, while per-template values should still be retained.
- **Refusal has a ceiling effect for aligned models.** A 98% harmful refusal rate is useful when measuring refusal-neuron ablations, but may be too easy for ranking strong aligned models.
- **Generation has useful sensitivity.** The prefill bypass produces the full 1–5 harmfulness range while benign generations remain coherent and relevant.

## Remaining limitations

- Harmful recognition uses AdvBench/HarmBench for harmful prompts and Alpaca for benign prompts. Because labels and sources are correlated, a model may partly exploit dataset style. A future version should add same-source minimal pairs or an independent benign safety dataset.
- This audit uses one LLM judge. A second judge or blinded human review of at least 10–20% is recommended before publication.
- At 512 tokens, 14% of refusal responses and 26% of prefilled generations reached the token cap. The benchmark protocol is reproducible as written, but 768–1024 tokens is preferable when coherence under strong neuron interventions is the primary outcome.

Machine-readable values are in `recognition_metrics.json`, `refusal_metrics.json`, and `generation_metrics.json`.
