# Sampling and reproducibility

This folder contains the supporting code for Tutorial 6 of the Local LLMs with
MLX series.

**Full tutorial:** [Link will be added after publication](TUTORIAL_URL)

The comparison script runs one fixed chat prompt under several sampling
profiles. It is designed to show how decoding settings change the response,
not to measure inference speed.

## Requirements

- An Apple silicon Mac running macOS 14 or newer
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/)
- The model snapshot selected in Tutorial 4, already present in the Hugging
  Face cache

## Set up the environment

From the repository root, install the locked dependencies:

```bash
uv sync --locked
```

The script uses the model and exact revision selected in Tutorial 4:

```text
Model:    mlx-community/Qwen2.5-0.5B-Instruct-4bit
Revision: a5339a4131f135d0fdc6a5c8b5bbed2753bbe0f3
```

## Compare the default profiles

Run every profile against the same prompt:

```bash
uv run python tutorials/06-sampling-and-reproducibility/compare_sampling.py
```

The script loads the model once, creates one chat-formatted prompt, resets the
same seed before each profile, and prints each response with the settings that
produced it. Exact wording is model-dependent; compare the response patterns,
not a fixed expected answer.

The included profiles are:

| Profile | Purpose | Settings |
| --- | --- | --- |
| `greedy` | Select the most likely next token at every step. | `temperature=0` |
| `focused` | Sample from a narrow, lower-randomness candidate set. | `temperature=0.3`, `top_p=0.9`, `top_k=40`, `min_p=0.05` |
| `diverse` | Permit more variation while still excluding the low-probability tail. | `temperature=0.8`, `top_p=0.95` |
| `repetition-aware` | Sample with a short recent-token penalty. | `temperature=0.7`, `top_p=0.9`, `top_k=40`, `min_p=0.02`, repetition penalty `1.1`, presence penalty `0.25` |

The profiles are illustrative starting points rather than universally good
settings. They deliberately combine some controls, so use the next section to
isolate a particular effect.

## Isolate one setting or profile

Run a subset with the same prompt and seed:

```bash
uv run python tutorials/06-sampling-and-reproducibility/compare_sampling.py \
  --prompt "Suggest three names for a small neighborhood bookshop." \
  --profiles greedy focused diverse \
  --seed 7 \
  --max-tokens 64
```

`temperature=0` makes the script use greedy decoding. A value above zero makes
it sample from the probability distribution. `top_p`, `top_k`, and `min_p`
then constrain which lower-probability tokens remain eligible before sampling.
The script passes these settings to MLX LM's `make_sampler` helper.

The `repetition-aware` profile also uses the installed version's supported
logits processors:

- A **repetition penalty** changes the score of recently repeated tokens.
- A **presence penalty** reduces the score of a token that has already appeared
  in the recent context.

These are token-level controls. They can reduce unwanted repetition, but they
can also make an answer less natural. Change one setting at a time when
evaluating output quality.

## Repeat the same run

Run one sampled profile twice with the same seed:

```bash
uv run python tutorials/06-sampling-and-reproducibility/compare_sampling.py \
  --profiles diverse \
  --runs 2 \
  --seed 7
```

The script resets `mlx.random` to the selected seed before every run, so the
two outputs should match when the model, revision, package versions, prompt,
and hardware environment remain the same. A seed makes an experiment easier to
repeat; it does not promise identical output after changing the model, MLX LM
version, or execution environment.

To explore a different sampled sequence, choose a different seed:

```bash
uv run python tutorials/06-sampling-and-reproducibility/compare_sampling.py \
  --profiles diverse \
  --seed 42
```

## Keep quality experiments separate from benchmarks

This script compares generated text. It keeps the model, prompt, maximum
output length, and initial seed fixed so that the sampling profile is the
intended variable. It does not record timings, throughput, or memory metrics,
and it should not be used to claim that one profile is faster than another.

Use the later benchmarking tutorial for performance measurements with warmups,
repeated runs, and an explicit measurement method.
