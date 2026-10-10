"""Generate one chat response with MLX LM and report basic runtime metrics."""

from __future__ import annotations

import argparse

from mlx_lm import generate, load, stream_generate


DEFAULT_MODEL = "mlx-community/Qwen2.5-0.5B-Instruct-4bit"
DEFAULT_REVISION = "a5339a4131f135d0fdc6a5c8b5bbed2753bbe0f3"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a response with a locally cached MLX model."
    )
    parser.add_argument("--prompt", required=True, help="The user's chat message.")
    parser.add_argument(
        "--system-prompt",
        default="You are a concise and helpful assistant.",
        help="Optional instruction placed before the user message.",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model ID or local path.")
    parser.add_argument(
        "--revision",
        default=DEFAULT_REVISION,
        help="Model revision to load when --model is a Hugging Face ID.",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=64,
        help="Maximum number of tokens to generate (default: 64).",
    )
    parser.add_argument(
        "--mode",
        choices=("stream", "generate"),
        default="stream",
        help="Print streamed text or collect the complete response (default: stream).",
    )
    args = parser.parse_args()
    if args.max_tokens <= 0:
        parser.error("--max-tokens must be greater than zero")
    return args


def build_prompt_tokens(tokenizer, system_prompt: str, user_prompt: str) -> list[int]:
    """Apply the model's chat template and return its token IDs."""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})
    return tokenizer.apply_chat_template(
        messages, tokenize=True, add_generation_prompt=True
    )


def print_metrics(response) -> None:
    print(
        "\n\nMetrics: "
        f"prompt={response.prompt_tokens} tokens "
        f"({response.prompt_tps:.1f} tokens/s), "
        f"generation={response.generation_tokens} tokens "
        f"({response.generation_tps:.1f} tokens/s), "
        f"peak_memory={response.peak_memory:.3f} GB"
    )


def main() -> None:
    args = parse_args()
    model, tokenizer = load(args.model, revision=args.revision)
    prompt_tokens = build_prompt_tokens(tokenizer, args.system_prompt, args.prompt)
    print(f"Prepared chat prompt: {len(prompt_tokens)} tokens")

    if args.mode == "generate":
        # generate() consumes the same stream internally, then returns one string.
        complete_response = generate(
            model,
            tokenizer,
            prompt_tokens,
            max_tokens=args.max_tokens,
            verbose=False,
        )
        print(f"Response: {complete_response}")
        return

    print("Response: ", end="", flush=True)
    final_response = None
    for response in stream_generate(
        model, tokenizer, prompt_tokens, max_tokens=args.max_tokens
    ):
        print(response.text, end="", flush=True)
        final_response = response

    if final_response is not None:
        print_metrics(final_response)


if __name__ == "__main__":
    main()
