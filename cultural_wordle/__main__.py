from __future__ import annotations

import argparse

from .solver import CulturalAlgorithmSolver
from .wordle import format_feedback


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cultural-wordle")
    parser.add_argument("--answer", required=True)
    parser.add_argument("--answers-file", default="short-list-of-words.txt")
    parser.add_argument("--allowed-file", default="long-list-of-words.txt")
    parser.add_argument("--max-guesses", type=int, default=6)
    parser.add_argument("--seed", type=int, default=7)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    solver = CulturalAlgorithmSolver.from_files(
        answers_path=args.answers_file,
        allowed_guesses_path=args.allowed_file,
        seed=args.seed,
    )
    result = solver.solve(args.answer.lower(), max_guesses=args.max_guesses)

    for turn, attempt in enumerate(result.guesses, start=1):
        print(f"{turn}. {attempt.guess} {format_feedback(attempt.feedback)}")

    if result.solved:
        print(f"Solved in {result.guess_count} guesses.")
    else:
        print(f"Failed to solve {result.answer} in {args.max_guesses} guesses.")


if __name__ == "__main__":
    main()
