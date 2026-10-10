# Finding and managing models with Hugging Face

This folder contains the supporting code for Tutorial 3 of the Local LLMs with
MLX series.

**Full tutorial:** [Link will be added after publication](TUTORIAL_URL)

The example searches the Hugging Face Hub for MLX-compatible models, inspects
a model before downloading it, pins a reproducible revision, verifies the
cached snapshot, tests offline access, and previews safe cache cleanup.

## Requirements

- An Apple silicon Mac running macOS 14 or newer
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/)
- An internet connection for model discovery, verification, and the initial
  download
- A Hugging Face account and access token only when using gated models

## Set up the environment

From the repository root, install the locked dependencies:

```bash
uv sync --locked
```

The commands below use the `hf` CLI provided by the project's pinned
`huggingface-hub` dependency. Check the installed version:

```bash
uv run hf version
```

## Search for an MLX model

Search the `mlx-community` organization for text-generation models whose names
contain `4bit`:

```bash
uv run hf models list \
  --author mlx-community \
  --pipeline-tag text-generation \
  --search 4bit \
  --sort downloads \
  --limit 10
```

This tutorial continues with the same small instruction-tuned model used in
Tutorial 2:

```text
mlx-community/Qwen2.5-0.5B-Instruct-4bit
```

## Inspect the model before downloading

Read the model card, metadata, and repository file tree:

```bash
uv run hf models card mlx-community/Qwen2.5-0.5B-Instruct-4bit --text
```

```bash
uv run hf models info \
  mlx-community/Qwen2.5-0.5B-Instruct-4bit \
  --expand sha,tags,usedStorage,safetensors,config \
  --format json
```

```bash
uv run hf models list \
  mlx-community/Qwen2.5-0.5B-Instruct-4bit \
  --tree \
  --human-readable
```

Before selecting a model, confirm that its repository contains MLX weights, a
tokenizer, a configuration file, and any chat template required by the model.
Also check its parameter count, quantization, context limit, license, and base
model.

The model name describes approximately 0.5 billion parameters and 4-bit weight
quantization. These properties influence resource use, but the model's download
size is not its total runtime memory requirement. Inference also uses memory for
the tokenizer, temporary activations, the KV cache, and the MLX allocator.

Preview the complete snapshot download without transferring files:

```bash
uv run hf download \
  mlx-community/Qwen2.5-0.5B-Instruct-4bit \
  --revision a5339a4131f135d0fdc6a5c8b5bbed2753bbe0f3 \
  --dry-run
```

## Authenticate for gated models

The example model is public and does not require authentication. For a gated
model, first accept its access conditions on the Hub and then sign in:

```bash
uv run hf auth login
uv run hf auth whoami
```

Do not commit a Hugging Face access token to the repository or place it directly
in a command saved to shell history.

## Download a pinned snapshot

Download the complete model at a specific commit instead of following the
mutable `main` branch:

```bash
uv run hf download \
  mlx-community/Qwen2.5-0.5B-Instruct-4bit \
  --revision a5339a4131f135d0fdc6a5c8b5bbed2753bbe0f3
```

The command prints the local snapshot path. Reusing the model ID and commit
hash gives the project a stable model revision even if `main` changes later.

## Inspect and verify the cache

List cached models, including the revisions stored on disk:

```bash
uv run hf cache list \
  --filter "type=model" \
  --revisions \
  --sort name
```

Ask MLX LM to show model repositories that it recognizes in the Hugging Face
cache:

```bash
uv run mlx_lm.manage --scan --pattern "mlx-community"
```

While online, compare the cached files with the pinned Hub revision:

```bash
uv run hf cache verify \
  mlx-community/Qwen2.5-0.5B-Instruct-4bit \
  --revision a5339a4131f135d0fdc6a5c8b5bbed2753bbe0f3 \
  --fail-on-missing-files
```

## Confirm offline access

After the snapshot is cached, force offline mode and resolve the same pinned
revision again:

```bash
HF_HUB_OFFLINE=1 uv run hf download \
  mlx-community/Qwen2.5-0.5B-Instruct-4bit \
  --revision a5339a4131f135d0fdc6a5c8b5bbed2753bbe0f3
```

This command should immediately print the existing snapshot path without making
a network request. A missing-file or missing-revision error means the requested
snapshot is not completely available in the local cache.

## Preview cache cleanup

Preview the removal of the example repository without deleting anything:

```bash
uv run hf cache rm \
  model/mlx-community/Qwen2.5-0.5B-Instruct-4bit \
  --dry-run
```

Preview removal of detached revisions and incomplete downloads:

```bash
uv run hf cache prune --dry-run
```

After reviewing the reported paths and sizes, omit `--dry-run` to start an
interactive deletion. Keep the cached snapshot if you plan to continue to the
next tutorial.
