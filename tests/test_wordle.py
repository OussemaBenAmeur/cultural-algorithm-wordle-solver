import unittest

from cultural_wordle import feedback_code, filter_candidates, format_feedback


class WordleRulesTest(unittest.TestCase):
    def test_feedback_handles_duplicate_letters(self) -> None:
        feedback = feedback_code("allee", "apple")
        self.assertEqual(format_feedback(feedback), "🟩🟨⬛⬛🟩")

    def test_feedback_all_green_for_exact_match(self) -> None:
        feedback = feedback_code("crane", "crane")
        self.assertEqual(format_feedback(feedback), "🟩🟩🟩🟩🟩")

    def test_filter_candidates_keeps_only_consistent_answers(self) -> None:
        candidates = ["slate", "plate", "place", "crone", "flame"]
        feedback = feedback_code("slimy", "slate")
        filtered = filter_candidates(candidates, "slimy", feedback)
        self.assertEqual(filtered, ["slate"])


if __name__ == "__main__":
    unittest.main()
