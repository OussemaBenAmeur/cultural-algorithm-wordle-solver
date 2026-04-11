from __future__ import annotations

import ast
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


Tile = int


@dataclass(frozen=True)
class Attempt:
    guess: str
    feedback: int


@lru_cache(maxsize=None)
def feedback_code(guess: str, answer: str) -> int:
    result = [0] * 5
    remaining = Counter()

    for index, (guess_letter, answer_letter) in enumerate(zip(guess, answer)):
        if guess_letter == answer_letter:
            result[index] = 2
        else:
            remaining[answer_letter] += 1

    for index, guess_letter in enumerate(guess):
        if result[index] != 0:
            continue
        if remaining[guess_letter] > 0:
            result[index] = 1
            remaining[guess_letter] -= 1

    code = 0
    for tile in result:
        code = code * 3 + tile
    return code


def decode_feedback(code: int) -> tuple[Tile, Tile, Tile, Tile, Tile]:
    values = [0] * 5
    current = code
    for index in range(4, -1, -1):
        values[index] = current % 3
        current //= 3
    return tuple(values)


def format_feedback(code: int) -> str:
    tiles = {0: "⬛", 1: "🟨", 2: "🟩"}
    return "".join(tiles[value] for value in decode_feedback(code))


def filter_candidates(candidates: list[str], guess: str, code: int) -> list[str]:
    return [candidate for candidate in candidates if feedback_code(guess, candidate) == code]


def load_words(path: str | Path) -> tuple[str, ...]:
    text = Path(path).read_text(encoding="utf-8").strip()
    if "=" in text and "[" in text and "]" in text:
        _, right_hand_side = text.split("=", 1)
        words = ast.literal_eval(right_hand_side.strip())
    else:
        words = [line.strip() for line in text.splitlines()]
    cleaned = []
    seen = set()
    for word in words:
        normalized = str(word).strip().lower()
        if len(normalized) != 5 or not normalized.isalpha() or normalized in seen:
            continue
        seen.add(normalized)
        cleaned.append(normalized)
    return tuple(cleaned)
