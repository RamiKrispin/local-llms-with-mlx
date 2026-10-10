# Getting started with MLX LM

This folder contains the supporting code for Tutorial 2 of the Local LLMs with
MLX series.

**Full tutorial:** [Link will be added after publication](TUTORIAL_URL)

The example creates the project environment, downloads a small MLX model, runs
the MLX LM server, and sends one chat-completion request.

## Requirements

- An Apple silicon Mac running macOS 14 or newer
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/)
- An internet connection for the initial setup and model download

## Set up the environment

### Use the supporting repository

From the repository root, install the locked dependencies:

```bash
uv sync --locked
```

The environment includes three main libraries:

- **MLX** provides the array and compute framework that runs operations on the
  Apple silicon GPU.
- **MLX LM** loads and runs the model and provides the local HTTP server.
- **Hugging Face Hub** provides the `hf` command used to download and cache the
  model files.

Verify that MLX can see the GPU:

```bash
uv run python -c 'import mlx.core as mx; print(mx.default_device())'
```

The verification command should print `Device(gpu, 0)`.

### Alternative: Create a standalone uv project

To run the example without cloning or forking the supporting repository,
create a minimal local project and add the same direct dependencies:

```bash
mkdir mlx-lm-hello-world
cd mlx-lm-hello-world

uv init --bare --python 3.12
uv python pin 3.12
uv add "mlx==0.32.2" "mlx-lm==0.31.3" "huggingface-hub==1.31.0"
```

The `uv python pin` command records Python 3.12 in `.python-version`. The
`uv add` command creates `.venv` and `uv.lock`, installs the dependencies, and
records their resolved versions. Verify the MLX device before continuing:

```bash
uv run python -c 'import mlx.core as mx; print(mx.default_device())'
```

The remaining commands work the same way from this standalone project.

## Download the model

Download the approximately 290 MB
[`mlx-community/Qwen2.5-0.5B-Instruct-4bit`](https://huggingface.co/mlx-community/Qwen2.5-0.5B-Instruct-4bit)
snapshot to the Hugging Face cache:

```bash
uv run hf download mlx-community/Qwen2.5-0.5B-Instruct-4bit
```

## Start the server

```bash
uv run mlx_lm.server \
  --model mlx-community/Qwen2.5-0.5B-Instruct-4bit \
  --host 127.0.0.1 \
  --port 8080 \
  --max-tokens 64
```

Leave the server running and open a second terminal for the request.

## Send a request

From the project directory in the second terminal, run:

```bash
curl --silent --show-error \
  http://127.0.0.1:8080/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Reply with exactly: Hello from MLX LM!"
      }
    ],
    "temperature": 0,
    "max_tokens": 32
  }' | uv run python -m json.tool
```

The generated text is returned in `choices[0].message.content`. Press
`Control-C` in the first terminal to stop the server.
