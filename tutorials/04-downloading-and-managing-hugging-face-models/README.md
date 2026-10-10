# Downloading and managing Hugging Face models locally

This folder contains the supporting code for Tutorial 4 of the Local LLMs with
MLX series.

**Full tutorial:** [Link will be added after publication](TUTORIAL_URL)

The example downloads the model selected in Tutorial 3 at a pinned revision,
inspects and verifies the Hugging Face cache, confirms that the model can be
resolved offline, and previews cache cleanup without deleting any files.

## Requirements

- An Apple silicon Mac running macOS 14 or newer
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/)
- An internet connection for the initial download and cache verification
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

This tutorial uses the model and revision selected in Tutorial 3:

```text
Model:    mlx-community/Qwen2.5-0.5B-Instruct-4bit
Revision: a5339a4131f135d0fdc6a5c8b5bbed2753bbe0f3
```

## Preview the download

Use `--dry-run` to list the files and total transfer size without downloading
anything:

```bash
uv run hf download \
  mlx-community/Qwen2.5-0.5B-Instruct-4bit \
  --revision a5339a4131f135d0fdc6a5c8b5bbed2753bbe0f3 \
  --dry-run
```

If the snapshot is already complete in the local cache, the command reports
that zero files need to be downloaded.

## Authenticate for a gated model

The example model is public and does not require authentication. For a gated
model, accept its access conditions on the model page and then sign in:

```bash
uv run hf auth login
uv run hf auth whoami
```

Do not commit a Hugging Face access token to the repository or include it in a
command saved to shell history.

## Download a pinned snapshot

Download the complete model at the selected commit instead of following the
mutable `main` branch:

```bash
uv run hf download \
  mlx-community/Qwen2.5-0.5B-Instruct-4bit \
  --revision a5339a4131f135d0fdc6a5c8b5bbed2753bbe0f3
```

The command prints the local snapshot path. Repeating it with the same model ID
and revision reuses the cached files instead of downloading duplicates.

## Inspect the local cache

List cached models and the revisions stored on disk:

```bash
uv run hf cache list \
  --filter "type=model" \
  --revisions \
  --sort name
```

Ask MLX LM to scan the Hugging Face cache for repositories from
`mlx-community`:

```bash
uv run mlx_lm.manage --scan --pattern "mlx-community"
```

The first command reports every matching cached revision. The second narrows
the view to model repositories that MLX LM can inspect.

## Verify the cached snapshot

While online, compare the cached files with the selected Hub revision:

```bash
uv run hf cache verify \
  mlx-community/Qwen2.5-0.5B-Instruct-4bit \
  --revision a5339a4131f135d0fdc6a5c8b5bbed2753bbe0f3 \
  --fail-on-missing-files
```

This check contacts the Hugging Face Hub to obtain the repository file list and
checksums. A missing or modified file causes the command to fail. Run the
pinned download command again to restore a missing or incomplete snapshot.

## Confirm offline access

After the snapshot is cached, enable offline mode and resolve the same pinned
revision:

```bash
HF_HUB_OFFLINE=1 uv run hf download \
  mlx-community/Qwen2.5-0.5B-Instruct-4bit \
  --revision a5339a4131f135d0fdc6a5c8b5bbed2753bbe0f3
```

The command should immediately print the existing snapshot path without making
a network request. A missing-revision or missing-file error means the requested
snapshot is not fully available in the local cache.

## Preview cache cleanup

Preview removal of the example model repository without deleting it:

```bash
uv run hf cache rm \
  model/mlx-community/Qwen2.5-0.5B-Instruct-4bit \
  --dry-run
```

Preview removal of detached revisions and incomplete downloads:

```bash
uv run hf cache prune --dry-run
```

Review the reported repositories, revisions, paths, and sizes before running a
cleanup command without `--dry-run`. Keep the example snapshot in the cache if
you plan to use it in Tutorial 5.
