from __future__ import annotations

import math
import random
from collections import Counter
from dataclasses import dataclass

from .wordle import Attempt, feedback_code, filter_candidates, load_words


@dataclass(frozen=True)
class SolveResult:
    answer: str
    solved: bool
    guesses: tuple[Attempt, ...]

    @property
    def guess_count(self) -> int:
        return len(self.guesses)

    @property
    def final_guess(self) -> str | None:
        if not self.guesses:
            return None
        return self.guesses[-1].guess


@dataclass
class BeliefSpace:
    position_probabilities: tuple[dict[str, float], ...]
    letter_probabilities: dict[str, float]
    situational_best: str | None
    situational_score: float
    historical: tuple[Attempt, ...]


class CulturalAlgorithmSolver:
    def __init__(
        self,
        answers: list[str] | tuple[str, ...],
        allowed_guesses: list[str] | tuple[str, ...] | None = None,
        *,
        population_size: int = 60,
        generations: int = 7,
        acceptance_ratio: float = 0.2,
        finalist_pool: int = 16,
        sample_size: int = 180,
        exploration_pool_size: int = 2200,
        seed: int = 7,
    ) -> None:
        self.answers = tuple(answers)
        self.allowed_guesses = tuple(allowed_guesses or answers)
        self.population_size = population_size
        self.generations = generations
        self.acceptance_ratio = acceptance_ratio
        self.finalist_pool = finalist_pool
        self.sample_size = sample_size
        self.exploration_pool_size = exploration_pool_size
        self.seed = seed
        self.allowed_guess_set = set(self.allowed_guesses)
        self.answer_set = set(self.answers)
        self.exploration_pool = self._build_exploration_pool()

    @classmethod
    def from_files(
        cls,
        answers_path: str,
        allowed_guesses_path: str | None = None,
        **kwargs: object,
    ) -> "CulturalAlgorithmSolver":
        answers = load_words(answers_path)
        allowed_guesses = load_words(allowed_guesses_path) if allowed_guesses_path else answers
        return cls(answers=answers, allowed_guesses=allowed_guesses, **kwargs)

    def solve(self, answer: str, max_guesses: int = 6) -> SolveResult:
        remaining_answers = list(self.answers)
        history: list[Attempt] = []
        random_source = random.Random(f"{self.seed}:{answer}")

        for _ in range(max_guesses):
            guess = self.select_guess(remaining_answers, history, random_source)
            code = feedback_code(guess, answer)
            attempt = Attempt(guess=guess, feedback=code)
            history.append(attempt)
            if guess == answer:
                return SolveResult(answer=answer, solved=True, guesses=tuple(history))
            remaining_answers = filter_candidates(remaining_answers, guess, code)
            if not remaining_answers:
                break

        return SolveResult(answer=answer, solved=False, guesses=tuple(history))

    def select_guess(
        self,
        feasible_answers: list[str],
        history: list[Attempt],
        random_source: random.Random,
    ) -> str:
        if len(feasible_answers) == 1:
            return feasible_answers[0]
        if len(feasible_answers) <= 8:
            return self._choose_endgame_guess(feasible_answers, history)

        population = self._initialize_population(feasible_answers, history, random_source)
        belief = self._build_belief(feasible_answers, (), history)
        situational_best = population[0]
        situational_score = float("-inf")

        for _ in range(self.generations):
            sample_answers = self._sample_answers(feasible_answers, random_source)
            scored_population = [
                (
                    self._fitness(word, feasible_answers, sample_answers, belief, len(history)),
                    word,
                )
                for word in population
            ]
            scored_population.sort(reverse=True)
            accepted_count = max(2, int(self.population_size * self.acceptance_ratio))
            accepted = tuple(scored_population[:accepted_count])
            if accepted[0][0] > situational_score:
                situational_score, situational_best = accepted[0]
            belief = self._build_belief(
                feasible_answers,
                accepted,
                history,
                situational_best=situational_best,
                situational_score=situational_score,
            )
            population = self._influence_population(feasible_answers, belief, accepted, history, random_source)

        finalists = self._collect_finalists(feasible_answers, belief, population, history)
        scored_finalists = [
            (
                self._final_score(word, feasible_answers, belief, len(history)),
                word,
            )
            for word in finalists
        ]
        scored_finalists.sort(reverse=True)
        return scored_finalists[0][1]

    def _sample_answers(self, feasible_answers: list[str], random_source: random.Random) -> list[str]:
        if len(feasible_answers) <= self.sample_size:
            return feasible_answers
        return random_source.sample(feasible_answers, self.sample_size)

    def _initialize_population(
        self,
        feasible_answers: list[str],
        history: list[Attempt],
        random_source: random.Random,
    ) -> list[str]:
        belief = self._build_belief(feasible_answers, (), history)
        ranked = self._rank_by_belief(feasible_answers, belief, allow_exploration=False)
        population: list[str] = []
        seen = set()

        for word in ranked[: min(len(ranked), self.population_size // 3)]:
            if word not in seen:
                population.append(word)
                seen.add(word)

        exploratory_ranked = self._rank_by_belief(self.exploration_pool, belief, allow_exploration=True)
        for word in exploratory_ranked[: self.population_size]:
            if word not in seen:
                population.append(word)
                seen.add(word)
            if len(population) >= self.population_size:
                return population

        pool = list(self.allowed_guesses)
        while len(population) < self.population_size:
            candidate = random_source.choice(pool)
            if candidate in seen:
                continue
            population.append(candidate)
            seen.add(candidate)
        return population

    def _build_belief(
        self,
        feasible_answers: list[str],
        accepted: tuple[tuple[float, str], ...],
        history: list[Attempt],
        situational_best: str | None = None,
        situational_score: float = float("-inf"),
    ) -> BeliefSpace:
        position_counts = [Counter() for _ in range(5)]
        letter_counts = Counter()
        base_weight = 1.0 / max(1, len(feasible_answers))

        for word in feasible_answers:
            for index, letter in enumerate(word):
                position_counts[index][letter] += base_weight
            for letter in set(word):
                letter_counts[letter] += base_weight

        accepted_count = max(1, len(accepted))
        for rank, (score, word) in enumerate(accepted, start=1):
            weight = 1.25 + (accepted_count - rank + 1) / accepted_count
            if score > 0:
                weight *= 1.0 + min(score / 10.0, 0.35)
            for index, letter in enumerate(word):
                position_counts[index][letter] += weight
            for letter in set(word):
                letter_counts[letter] += weight

        position_probabilities = []
        for counter in position_counts:
            total = sum(counter.values()) or 1.0
            position_probabilities.append({letter: value / total for letter, value in counter.items()})

        total_letters = sum(letter_counts.values()) or 1.0
        letter_probabilities = {letter: value / total_letters for letter, value in letter_counts.items()}

        return BeliefSpace(
            position_probabilities=tuple(position_probabilities),
            letter_probabilities=letter_probabilities,
            situational_best=situational_best,
            situational_score=situational_score,
            historical=tuple(history),
        )

    def _rank_by_belief(
        self,
        words: list[str] | tuple[str, ...],
        belief: BeliefSpace,
        *,
        allow_exploration: bool,
    ) -> list[str]:
        return sorted(
            words,
            key=lambda word: (
                self._alignment_score(word, belief, allow_exploration=allow_exploration),
                word in self.answer_set,
            ),
            reverse=True,
        )

    def _alignment_score(self, word: str, belief: BeliefSpace, *, allow_exploration: bool) -> float:
        unique_letters = set(word)
        position_score = sum(
            belief.position_probabilities[index].get(letter, 0.0)
            for index, letter in enumerate(word)
        )
        letter_score = sum(belief.letter_probabilities.get(letter, 0.0) for letter in unique_letters)
        duplicate_penalty = (len(word) - len(unique_letters)) * (0.12 if allow_exploration else 0.04)
        situational_bonus = 0.0
        if belief.situational_best:
            situational_bonus = sum(
                0.05 for index, letter in enumerate(word) if belief.situational_best[index] == letter
            )
        return position_score * 0.58 + letter_score * 0.42 + situational_bonus - duplicate_penalty

    def _fitness(
        self,
        word: str,
        feasible_answers: list[str],
        sample_answers: list[str],
        belief: BeliefSpace,
        turn_index: int,
    ) -> float:
        entropy, worst_share, partition_count = self._partition_metrics(word, sample_answers)
        alignment = self._alignment_score(word, belief, allow_exploration=True)
        answer_bonus = 0.0
        if word in feasible_answers:
            answer_bonus += 0.35
            if len(feasible_answers) <= 12:
                answer_bonus += 0.5
            if len(feasible_answers) <= 5:
                answer_bonus += 0.75
        novelty_bonus = 0.0
        guessed_letters = {letter for attempt in belief.historical for letter in set(attempt.guess)}
        novel_letters = len(set(word) - guessed_letters)
        if len(feasible_answers) > 15:
            novelty_bonus = novel_letters * 0.05
        patience_penalty = turn_index * 0.02 if word not in feasible_answers else 0.0
        return (
            entropy * 1.9
            - worst_share * 1.1
            + partition_count / max(1, len(sample_answers)) * 0.35
            + alignment * 0.55
            + answer_bonus
            + novelty_bonus
            - patience_penalty
        )

    def _influence_population(
        self,
        feasible_answers: list[str],
        belief: BeliefSpace,
        accepted: tuple[tuple[float, str], ...],
        history: list[Attempt],
        random_source: random.Random,
    ) -> list[str]:
        next_population: list[str] = []
        seen = set()

        for _, word in accepted:
            if word not in seen:
                next_population.append(word)
                seen.add(word)

        if belief.situational_best and belief.situational_best not in seen:
            next_population.append(belief.situational_best)
            seen.add(belief.situational_best)

        guided = self._rank_by_belief(self.exploration_pool, belief, allow_exploration=True)
        for word in guided[: self.population_size * 2]:
            if word not in seen:
                next_population.append(word)
                seen.add(word)
            if len(next_population) >= self.population_size // 2:
                break

        crossover_pool = [word for _, word in accepted[: min(6, len(accepted))]]
        while len(next_population) < self.population_size and crossover_pool:
            parent_a = random_source.choice(crossover_pool)
            parent_b = random_source.choice(crossover_pool)
            template = tuple(
                parent_a[index] if random_source.random() < 0.5 else parent_b[index]
                for index in range(5)
            )
            child = self._best_template_match(template, guided, feasible_answers)
            if child not in seen:
                next_population.append(child)
                seen.add(child)
                continue
            fallback = guided[random_source.randrange(min(len(guided), 120))]
            if fallback not in seen:
                next_population.append(fallback)
                seen.add(fallback)

        feasible_ranked = self._rank_by_belief(feasible_answers, belief, allow_exploration=False)
        for word in feasible_ranked:
            if word in seen:
                continue
            next_population.append(word)
            seen.add(word)
            if len(next_population) >= self.population_size:
                break

        while len(next_population) < self.population_size:
            candidate = random_source.choice(self.exploration_pool)
            if candidate in seen:
                continue
            next_population.append(candidate)
            seen.add(candidate)

        return next_population

    def _best_template_match(
        self,
        template: tuple[str, str, str, str, str],
        ranked_words: list[str],
        feasible_answers: list[str],
    ) -> str:
        best_word = feasible_answers[0] if feasible_answers else ranked_words[0]
        best_score = -1.0
        feasible_set = set(feasible_answers)
        for word in ranked_words[:180]:
            score = sum(1 for index, letter in enumerate(word) if template[index] == letter)
            if word in feasible_set:
                score += 0.75
            if len(set(word)) == 5:
                score += 0.15
            if score > best_score:
                best_word = word
                best_score = score
        return best_word

    def _collect_finalists(
        self,
        feasible_answers: list[str],
        belief: BeliefSpace,
        population: list[str],
        history: list[Attempt],
    ) -> list[str]:
        finalists: list[str] = []
        seen = set()

        def add(word: str) -> None:
            if word not in seen:
                finalists.append(word)
                seen.add(word)

        if belief.situational_best:
            add(belief.situational_best)

        for word in self._rank_by_belief(feasible_answers, belief, allow_exploration=False)[: self.finalist_pool]:
            add(word)

        for word in self._rank_by_belief(self.exploration_pool, belief, allow_exploration=True)[: self.finalist_pool]:
            add(word)

        for word in population[: self.finalist_pool]:
            add(word)

        if history:
            unseen_candidates = [
                word
                for word in feasible_answers
                if word not in {attempt.guess for attempt in history}
            ]
            for word in unseen_candidates[: self.finalist_pool]:
                add(word)

        return finalists

    def _final_score(
        self,
        word: str,
        feasible_answers: list[str],
        belief: BeliefSpace,
        turn_index: int,
    ) -> float:
        entropy, worst_share, partition_count = self._partition_metrics(word, feasible_answers)
        alignment = self._alignment_score(word, belief, allow_exploration=False)
        answer_bonus = 0.6 if word in feasible_answers else 0.0
        if len(feasible_answers) <= 6 and word in feasible_answers:
            answer_bonus += 0.9
        if len(feasible_answers) <= 3 and word in feasible_answers:
            answer_bonus += 1.0
        non_answer_penalty = 0.08 * turn_index if word not in feasible_answers else 0.0
        return (
            entropy * 2.1
            - worst_share * 1.55
            + partition_count / max(1, len(feasible_answers)) * 0.45
            + alignment * 0.3
            + answer_bonus
            - non_answer_penalty
        )

    def _partition_metrics(self, guess: str, answers: list[str]) -> tuple[float, float, int]:
        partitions: Counter[int] = Counter()
        for answer in answers:
            partitions[feedback_code(guess, answer)] += 1
        total = len(answers)
        if total == 0:
            return 0.0, 1.0, 0
        entropy = 0.0
        largest = 0
        for size in partitions.values():
            probability = size / total
            entropy -= probability * math.log2(probability)
            if size > largest:
                largest = size
        return entropy, largest / total, len(partitions)

    def _choose_endgame_guess(self, feasible_answers: list[str], history: list[Attempt]) -> str:
        guessed_words = {attempt.guess for attempt in history}
        feasible_set = set(feasible_answers)
        best_guess = feasible_answers[0]
        best_key: tuple[float, float, int, int, float, str] | None = None

        for guess in self.allowed_guesses:
            partitions: Counter[int] = Counter()
            for answer in feasible_answers:
                partitions[feedback_code(guess, answer)] += 1
            largest_bucket = max(partitions.values())
            expected_bucket = sum(size * size for size in partitions.values()) / len(feasible_answers)
            entropy = 0.0
            for size in partitions.values():
                probability = size / len(feasible_answers)
                entropy -= probability * math.log2(probability)
            key = (
                float(largest_bucket),
                expected_bucket,
                int(guess not in feasible_set),
                int(guess in guessed_words),
                -entropy,
                guess,
            )
            if best_key is None or key < best_key:
                best_key = key
                best_guess = guess

        return best_guess

    def _build_exploration_pool(self) -> tuple[str, ...]:
        position_counts = [Counter() for _ in range(5)]
        letter_counts = Counter()

        for word in self.answers:
            for index, letter in enumerate(word):
                position_counts[index][letter] += 1
            for letter in set(word):
                letter_counts[letter] += 1

        ranked = sorted(
            self.allowed_guesses,
            key=lambda word: (
                sum(position_counts[index][letter] for index, letter in enumerate(word)) * 0.6
                + sum(letter_counts[letter] for letter in set(word)) * 0.4
                - (len(word) - len(set(word))) * len(self.answers) * 0.15
                + (word in self.answer_set) * len(self.answers) * 0.05
            ),
            reverse=True,
        )
        pool = ranked[: min(len(ranked), self.exploration_pool_size)]
        return tuple(dict.fromkeys((*self.answers, *pool)))
