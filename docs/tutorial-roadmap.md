# Local LLMs with MLX: Tutorial Roadmap

This series teaches how to run, understand, measure, optimize, and serve local large language models on Apple silicon with MLX and MLX LM. It begins with a first successful generation, then opens up the inference pipeline so that performance and memory tuning are based on measurements rather than guesswork.

## Audience

The tutorials are intended for Python developers who are new to MLX or local LLM inference. Readers should be comfortable using a terminal, Python virtual environments, and basic Python scripts. Prior experience training neural networks is not required.

## Learning outcomes

By the end of the core series, readers should be able to:

- Explain the roles of MLX, MLX LM, and the Hugging Face Hub.
- Find, inspect, download, cache, and remove compatible models.
- Run text generation through both the MLX LM CLI and Python API.
- Explain tokenization, prefill, the KV cache, and autoregressive decoding.
- Measure time to first token, throughput, and peak memory correctly.
- Select model, context, cache, and generation settings for a particular hardware budget.
- Run a reusable local inference service and call its OpenAI-compatible API.
- Operate entirely offline after the required model artifacts are cached.

## Series overview

| Part | Tutorials | Main outcome |
| --- | --- | --- |
| 1. Foundations | 1–2 | Install the tools and manage models reliably. |
| 2. First inference | 3–5 | Generate text and control sampling and context. |
| 3. Architecture | 6–7 | Understand how MLX executes an inference request. |
| 4. Performance | 8–10 | Measure and optimize latency, throughput, and memory. |
| 5. Applications | 11–13 | Build a reusable service, server, and local chat application. |

## Tutorial estimates

The word estimates cover the explanatory narrative but exclude code listings, commands, and generated output. Learner time includes reading, running the examples, and completing the main exercise. It does not include model downloads or unusually long benchmark runs, which depend on network speed, model size, and hardware.

| # | Tutorial | Description | Estimated words | Learner time |
| ---: | --- | --- | ---: | ---: |
| 1 | MLX and MLX LM from zero | Install the project and standalone CLI, understand the toolchain, and verify the environment. | 1,400–1,800 | 25–40 min |
| 2 | Finding and managing models with Hugging Face | Search, inspect, download, cache, verify, and remove MLX-compatible models. | 1,800–2,300 | 35–50 min |
| 3 | Generate the first response | Load a model and tokenizer, prepare a chat prompt, and generate or stream text. | 1,800–2,400 | 35–55 min |
| 4 | Sampling and reproducibility | Compare decoding strategies and tune the balance between predictable and diverse output. | 1,600–2,200 | 30–45 min |
| 5 | Context windows and conversations | Measure token usage and manage conversation history within a safe context budget. | 2,000–2,700 | 40–60 min |
| 6 | How MLX works on Apple silicon | Explore unified memory, lazy evaluation, synchronization, streams, and MLX memory counters. | 2,200–3,000 | 40–60 min |
| 7 | Anatomy of an inference request | Trace a request through templating, tokenization, prefill, KV caching, decoding, and detokenization. | 2,200–3,000 | 40–60 min |
| 8 | Benchmarking local inference correctly | Build repeatable measurements for latency, throughput, and memory across cold and warm runs. | 2,500–3,200 | 50–75 min |
| 9 | Where inference memory goes | Account for weights, activations, the KV cache, allocator caching, and non-MLX process memory. | 2,200–3,000 | 45–65 min |
| 10 | Tune generation for the hardware budget | Tune model, prefill, KV-cache, context, and decoding settings against explicit performance goals. | 3,000–4,000 | 60–90 min |
| 11 | Build a reusable local generation engine | Turn a one-shot script into a configurable, reusable, offline-capable Python component. | 2,500–3,300 | 55–80 min |
| 12 | Serve a model with the MLX LM server | Start a local HTTP server, stream requests from clients, and manage its operational boundaries. | 2,500–3,300 | 55–80 min |
| 13 | Capstone: a local, offline chat application | Combine model discovery, inference, context management, metrics, streaming, and serving. | 3,500–5,000 | 90–120 min |

Tutorial 10 and the capstone are intentionally longer project-style lessons. If the implementation becomes dense, split Tutorial 10 into measurement and optimization parts, and split the capstone into engine, interface, and validation milestones.

## Part 1: Foundations

### Tutorial 1 — MLX and MLX LM from zero

**Goal:** Set up a reproducible development environment and understand the tools in the stack.

Topics:

- What MLX is and how MLX LM builds on it.
- Apple silicon and operating-system requirements.
- The roles of Python, `uv`, MLX LM, and the Hugging Face Hub.
- Project installation versus installing `mlx-lm` as a standalone CLI tool.
- Making the CLI permanently available on `PATH` with `uv tool update-shell`.
- Verifying the installation and troubleshooting Python interpreter selection.

Hands-on outcome: a working project environment plus globally accessible MLX LM commands.

### Tutorial 2 — Finding and managing models with Hugging Face

**Goal:** Choose and manage a model before loading it into memory.

Topics:

- Searching for MLX-compatible text-generation models with the `hf` CLI.
- Reading model cards, configuration, parameter counts, file sizes, quantization, and context limits.
- Understanding model parameters versus download size and runtime memory.
- Authentication and gated repositories.
- Downloading a complete model snapshot and pinning a revision for reproducibility.
- Inspecting the Hugging Face cache and listing locally available models.
- Running in offline mode and diagnosing incomplete snapshots.
- Removing unused cached models safely.
- Using `mlx_lm.manage` to inspect models recognized by MLX LM.

Hands-on outcome: a selected model downloaded locally and verified for offline use.

## Part 2: First inference

### Tutorial 3 — Generate the first response

**Goal:** Run a model through both the CLI and Python API.

Topics:

- Loading a model and tokenizer with `mlx_lm.load`.
- Why the model and tokenizer are separate objects.
- Turning chat messages into a prompt with the model's chat template.
- Tokenization, special tokens, end-of-sequence handling, and detokenization.
- Generating with `generate` and streaming with `stream_generate`.
- Controlling output length with `max_tokens`.
- Reading prompt rate, generation rate, and memory metrics.

Hands-on outcome: a small script that accepts a prompt and streams a response with basic metrics.

### Tutorial 4 — Sampling and reproducibility

**Goal:** Control the tradeoff between deterministic, focused, and diverse output.

Topics:

- Greedy decoding and probabilistic sampling.
- Temperature, `top_p`, `top_k`, and `min_p`.
- Repetition and presence-style penalties supported by the installed MLX LM version.
- Random seeds and the limits of deterministic execution.
- Separating generation-quality experiments from performance benchmarks.

Hands-on outcome: a comparison script that runs the same prompt under several sampling profiles.

### Tutorial 5 — Context windows and conversations

**Goal:** Manage prompt history without exceeding the model or memory budget.

Topics:

- The model's native context window and where to find it in configuration and documentation.
- The relationship between system prompt, conversation history, current input, and generated output.
- Measuring token counts before generation.
- Why editing `max_position_embeddings` does not retrain or safely extend a model.
- Truncation, sliding windows, summarization, and message-selection strategies.
- How longer context increases prefill work and KV-cache memory.
- Preserving important instructions when trimming a conversation.

Hands-on outcome: a conversation helper that enforces an explicit context budget.

## Part 3: Architecture

### Tutorial 6 — How MLX works on Apple silicon

**Goal:** Build the mental model needed to reason about MLX performance.

Topics:

- Unified memory and what CPU and GPU sharing memory does—and does not—mean.
- MLX arrays and selecting CPU or Metal GPU execution.
- Lazy evaluation, computation graphs, and the role of `mx.eval`.
- Synchronization and why timing asynchronous work can produce misleading results.
- Streams and compiled computation.
- Active, cached, and peak MLX memory.
- Memory pressure, compression, and swap at the operating-system level.

Hands-on outcome: a small MLX experiment demonstrating lazy execution, synchronization, and memory counters.

### Tutorial 7 — Anatomy of an inference request

**Goal:** Follow one request from user text to generated response.

Pipeline:

1. Resolve and load model weights and configuration.
2. Apply the chat template.
3. Tokenize the prompt.
4. Prefill the model and create the KV cache.
5. Produce logits and sample the next token.
6. Append to the KV cache and repeat the decode step.
7. Detokenize and stream or return the response.

Topics:

- What happens once at model load, once per request, and once per generated token.
- The difference between prefill and autoregressive decoding.
- Why time to first token and tokens per second describe different phases.
- How prompt length and requested output length affect total latency differently.

Hands-on outcome: an instrumented request that reports load time, prefill speed, time to first token, decode speed, and total latency.

## Part 4: Performance and memory

### Tutorial 8 — Benchmarking local inference correctly

**Goal:** Create repeatable measurements before attempting optimization.

Topics:

- Cold starts versus warm runs.
- Model load time, time to first token, prompt throughput, generation throughput, and end-to-end latency.
- Fixed prompts, fixed output lengths, warmups, repeated runs, and median results.
- Synchronizing MLX work before recording timings.
- Active, cached, and peak memory measurements.
- Thermal throttling, background applications, and macOS memory pressure.
- Recording hardware, software versions, model revision, and configuration with each benchmark.

Hands-on outcome: a reusable benchmark harness that writes comparable results.

### Tutorial 9 — Where inference memory goes

**Goal:** Account for memory used during model loading, prefill, and decoding.

Topics:

- Model weights and quantization metadata.
- Temporary activations and prefill working memory.
- KV-cache growth with layers, sequence length, batch size, and data type.
- Allocator cache versus actively used memory.
- Python, tokenizer, and other non-MLX process memory.
- Disk size versus runtime memory versus peak memory.
- Why exceeding physical memory can cause compression, swap, and severe slowdown.

Hands-on outcome: a memory profile showing how prompt and output lengths change peak and steady-state usage.

### Tutorial 10 — Tune generation for the hardware budget

**Goal:** Select settings according to a measurable optimization target.

Topics:

- Choosing model size and weight quantization.
- Prompt length and `prefill_step_size`.
- Output length and `max_tokens`.
- KV-cache quantization with `kv_bits` and `quantized_kv_start`.
- Bounding retained cache with `max_kv_size`, when supported by the chosen API.
- Prompt caching and reuse across requests.
- Speculative decoding.
- Batch size, concurrency, streaming, compilation, and warmup.
- Tuning separately for startup time, time to first token, prompt throughput, decode throughput, peak memory, long context, and concurrent users.
- Checking quality after memory-saving or approximate optimizations.

Hands-on outcome: a before-and-after tuning report for at least two goals, such as lowest peak memory and fastest interactive response.

## Part 5: Applications and serving

### Tutorial 11 — Build a reusable local generation engine

**Goal:** Move from a one-shot script to an application component.

Topics:

- Loading the model once and reusing it across requests.
- Separating model configuration, request configuration, and sampling configuration.
- Context-budget enforcement and conversation state.
- Streaming, cancellation, errors, and runtime metrics.
- Offline startup and actionable missing-model errors.
- Choosing safe defaults for local applications.

Hands-on outcome: a reusable Python generation class with a small command-line interface.

### Tutorial 12 — Serve a model with the MLX LM server

**Goal:** Expose local generation through an HTTP API.

Topics:

- Starting `mlx_lm.server` with a Hub model or local snapshot.
- Starting the server without network access.
- Sending chat-completion requests with `curl` and an OpenAI-compatible Python client.
- Streaming responses and passing request-level generation settings.
- Context limits, prompt caching, batching, concurrency, and memory behavior.
- Logging, health checks, process lifecycle, and binding to localhost.
- The development-oriented security and operational limits of the built-in server.

Hands-on outcome: a local server plus a separate client that streams a response and reports latency.

### Tutorial 13 — Capstone: a local, offline chat application

**Goal:** Combine model management, inference, measurement, and serving into one application.

Suggested features:

- Select among locally available models.
- Operate without internet access.
- Stream generated text.
- Maintain conversation history within a context budget.
- Display time to first token, generation rate, and peak memory.
- Switch between direct in-process inference and the MLX LM server backend.
- Provide clear errors for missing or incomplete model snapshots.

Hands-on outcome: a terminal or lightweight web chat application that demonstrates the full series.

## Optional advanced tutorials

These topics should follow the core series so they do not distract from the inference fundamentals:

- Convert supported Hugging Face models to MLX format.
- Quantize a model and compare size, speed, memory, and quality.
- Fine-tune with LoRA and evaluate the adapter.
- Evaluate models with perplexity and task-specific test sets.
- Produce structured output and integrate tool calling.
- Build a retrieval-augmented generation application.
- Run distributed inference or fine-tuning across multiple machines.
- Explore multimodal models with the appropriate MLX ecosystem tools.

## Suggested repository organization

```text
local-llms-with-mlx/
├── docs/
│   └── tutorial-roadmap.md
├── tutorials/
│   ├── 01-mlx-and-mlx-lm/
│   ├── 02-hugging-face-models/
│   └── ...
├── examples/
├── benchmarks/
├── assets/
├── pyproject.toml
└── README.md
```

Each tutorial folder can contain a `README.md`, one or more runnable examples, and any expected benchmark output. Shared helpers should move into a package only after at least two tutorials need them; keeping early examples self-contained makes the learning path easier to follow.

## Principles for the series

- **Start with a working result.** Introduce internals after readers have generated text successfully.
- **Measure before tuning.** Every performance recommendation should identify the metric it is expected to improve.
- **Separate phases.** Report model loading, prefill, and decoding independently.
- **Separate storage from memory.** Model download size, active memory, allocator cache, and process memory are different measurements.
- **Prefer reproducible examples.** Pin important versions and model revisions, and record the complete benchmark configuration.
- **Treat offline operation as a feature.** Verify the complete model snapshot before disconnecting from the network.
- **Keep quality in the loop.** Faster or smaller configurations are useful only when their output remains acceptable for the target task.
- **State security boundaries.** A convenient local development server is not automatically a production-ready service.
