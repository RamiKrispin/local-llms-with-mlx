"""Compare MLX LM sampling profiles with a fixed chat prompt."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass

import mlx.core as mx
from mlx_lm import generate, load
from mlx_lm.sample_utils import make_logits_processors, make_sampler


DEFAULT_MODEL = "mlx-community/Qwen2.5-0.5B-Instruct-4bit"
DEFAULT_REVISION = "a5339a4131f135d0fdc6a5c8b5bbed2753bbe0f3"


@dataclass(frozen=True)
class SamplingProfile:
    temperature: float
    top_p: float = 0.0
    top_k: int = 0
    min_p: float = 0.0
    repetition_penalty: float | None = None
    presence_penalty: float | None = None


PROFILES = {
    "greedy": SamplingProfile(temperature=0.0),
    "focused": SamplingProfile(
        temperature=0.3, top_p=0.9, top_k=40, min_p=0.05
    ),
    "diverse": SamplingProfile(temperature=0.8, top_p=0.95),
    "repetition-aware": SamplingProfile(
        temperature=0.7,
        top_p=0.9,
        top_k=40,
        min_p=0.02,
        repetition_penalty=1.1,
        presence_penalty=0.25,
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare sampling profiles with the same MLX LM chat prompt."
    )
    parser.add_argument(
        "--prompt",
        default="Write a short bedtime story about a curious robot and a paper kite.",
        help="User message used for every profile.",
    )
    parser.add_argument(
        "--system-prompt",
        default="You are a concise and imaginative assistant.",
        help="Optional instruction placed before the user message.",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model ID or local path.")
    parser.add_argument(
        "--revision",
        default=DEFAULT_REVISION,
        help="Model revision to load when --model is a Hugging Face ID.",
    )
    parser.add_argument(
        "--profiles",
        nargs="+",
        choices=tuple(PROFILES),
        default=tuple(PROFILES),
        help="Profiles to compare (default: all profiles).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=7,
        help="Random seed reset before every profile run (default: 7).",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="Runs per profile with the same seed (default: 1).",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=96,
        help="Maximum output tokens per run (default: 96).",
    )
    args = parser.parse_args()
    if args.runs <= 0:
        parser.error("--runs must be greater than zero")
    if args.max_tokens <= 0:
        parser.error("--max-tokens must be greater than zero")
    return args


def build_prompt_tokens(tokenizer, system_prompt: str, user_prompt: str) -> list[int]:
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})
    return tokenizer.apply_chat_template(
        messages, tokenize=True, add_generation_prompt=True
    )


def generate_with_profile(
    model, tokenizer, prompt_tokens, profile: SamplingProfile, max_tokens: int
) -> str:
    sampler = make_sampler(
        temp=profile.temperature,
        top_p=profile.top_p,
        top_k=profile.top_k,
        min_p=profile.min_p,
    )
    logits_processors = make_logits_processors(
        repetition_penalty=profile.repetition_penalty,
        presence_penalty=profile.presence_penalty,
    )
    return generate(
        model,
        tokenizer,
        prompt_tokens,
        max_tokens=max_tokens,
        sampler=sampler,
        logits_processors=logits_processors,
        verbose=False,
    )


def main() -> None:
    args = parse_args()
    model, tokenizer = load(args.model, revision=args.revision)
    prompt_tokens = build_prompt_tokens(tokenizer, args.system_prompt, args.prompt)
    print(f"Prompt: {len(prompt_tokens)} tokens")
    print("Each profile uses the same prompt, output limit, and initial seed.")

    for profile_name in args.profiles:
        profile = PROFILES[profile_name]
        for run_number in range(1, args.runs + 1):
            mx.random.seed(args.seed)
            response = generate_with_profile(
                model, tokenizer, prompt_tokens, profile, args.max_tokens
            )
            print(f"\n## {profile_name} (run {run_number}, seed {args.seed})")
            print(json.dumps(asdict(profile), sort_keys=True))
            print(response)


if __name__ == "__main__":
    main()
