# Generating the first response

This folder contains the supporting code for Tutorial 5 of the Local LLMs with
MLX series.

**Full tutorial:** [Link will be added after publication](TUTORIAL_URL)

This example loads the model selected in Tutorial 4, formats a chat request,
and generates a response through the MLX LM CLI and Python API. The Python
script streams output and reports prompt throughput, generation throughput,
and peak MLX memory.

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

This tutorial uses the model and revision selected and downloaded in Tutorial
4:

```text
Model:    mlx-community/Qwen2.5-0.5B-Instruct-4bit
Revision: a5339a4131f135d0fdc6a5c8b5bbed2753bbe0f3
```

## Generate with the CLI

The `mlx_lm.generate` command loads the model, applies its default chat
template, tokenizes the request, generates a response, and detokenizes the
output:

```bash
uv run mlx_lm.generate \
  --model mlx-community/Qwen2.5-0.5B-Instruct-4bit \
  --prompt "Explain why a tokenizer is needed before an LLM can generate text." \
  --max-tokens 64
```

By default, MLX LM prints the response and timing information. The CLI uses
the model repository from the local Hugging Face cache when it is available.
The Python example below passes the exact revision selected in Tutorial 4.

## Run the streaming Python example

Run the script from the repository root:

```bash
uv run python tutorials/05-generating-the-first-response/first_response.py \
  --prompt "Give a two-sentence explanation of MLX LM." \
  --max-tokens 64
```

The script performs these steps:

- `load` returns two separate objects: the model, which computes next-token
  probabilities, and the tokenizer, which translates between text and tokens.
- `apply_chat_template` turns structured chat messages into the model-specific
  prompt, including any special tokens required by that model.
- The template output is tokenized before `stream_generate` receives it. MLX
  LM stops when it encounters an end-of-sequence token or reaches
  `--max-tokens`.
- Each streamed response segment is detokenized and printed immediately. The
  final response provides prompt tokens per second, generation tokens per
  second, and peak memory in GB.

To receive the complete response after generation rather than streamed text,
choose the script's `generate` mode:

```bash
uv run python tutorials/05-generating-the-first-response/first_response.py \
  --prompt "Give a two-sentence explanation of MLX LM." \
  --max-tokens 64 \
  --mode generate
```

`generate` collects the same streaming steps internally and returns the whole
string after completion. Use the default streaming mode when you also want the
per-run throughput and peak-memory metrics.

## Use a different prompt or model

Pass a different prompt with `--prompt` and, when needed, a system instruction
with `--system-prompt`:

```bash
uv run python tutorials/05-generating-the-first-response/first_response.py \
  --system-prompt "Answer clearly and use no more than three sentences." \
  --prompt "What is a context window?" \
  --max-tokens 96
```

The default model ID and revision reproduce the Tutorial 4 selection. To try a
different local or Hub model, pass both `--model` and, when reproducibility
matters, `--revision`. Ensure that the model has a chat template before relying
on `apply_chat_template`.
