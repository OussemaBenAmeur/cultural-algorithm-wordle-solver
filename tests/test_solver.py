import unittest

from cultural_wordle import CulturalAlgorithmSolver, load_words


class SolverTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.answers = load_words("short-list-of-words.txt")
        cls.allowed_guesses = load_words("long-list-of-words.txt")
        cls.solver = CulturalAlgorithmSolver(
            answers=cls.answers,
            allowed_guesses=cls.allowed_guesses,
            population_size=60,
            generations=7,
            acceptance_ratio=0.2,
            finalist_pool=16,
            sample_size=180,
            seed=7,
        )

    def test_solver_handles_repeated_and_rare_letters(self) -> None:
        targets = ["cigar", "jazzy", "fuzzy", "nymph", "queue", "error", "sissy", "zesty"]
        for target in targets:
            with self.subTest(target=target):
                result = self.solver.solve(target, max_guesses=6)
                self.assertTrue(result.solved)
                self.assertEqual(result.final_guess, target)
                self.assertLessEqual(result.guess_count, 6)

    def test_solver_is_stable_on_spread_sample(self) -> None:
        sample_indexes = [0, 17, 53, 101, 207, 319, 451, 607, 809, 997, 1211, 1417, 1561, 1624]
        for index in sample_indexes:
            target = self.answers[index]
            with self.subTest(target=target):
                result = self.solver.solve(target, max_guesses=6)
                self.assertTrue(result.solved)
                self.assertEqual(result.final_guess, target)


if __name__ == "__main__":
    unittest.main()
