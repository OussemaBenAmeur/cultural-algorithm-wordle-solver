# Cultural Algorithm Wordle Solver

A clean Wordle solver built around an actual cultural algorithm, not a direct hidden-word fitness trick.

`crate ⬛🟨⬛⬛🟩 -> carol 🟩🟨⬛⬛⬛ -> cigar 🟩🟩🟩🟩🟩`

## What makes it a genuine cultural algorithm

- The population space is a changing set of candidate guesses.
- The belief space stores shared knowledge from play: positional letter beliefs, overall letter beliefs, the current best situational guess, and the full feedback history.
- An acceptance step keeps elite guesses from each generation.
- A belief update step learns from those elites and from the remaining feasible answers.
- An influence step uses that belief space to generate the next population.

The solver only learns through real Wordle feedback and candidate filtering. It does not score guesses by peeking at the target word.

## Repository layout

- `cultural_wordle/`: solver package and CLI
- `tests/`: unit tests for Wordle rules and solver behavior
- `short-list-of-words.txt`: answer list
- `long-list-of-words.txt`: allowed guess list
- `worlde-solver.ipynb`: original notebook prototype

## Run it

```bash
python3 -m cultural_wordle --answer jazzy
```

## Test it

```bash
python3 -m unittest -v
```

## Verification

- Unit tests cover duplicate-letter feedback, candidate filtering, and deterministic solver behavior.
- An exhaustive benchmark over all 1,625 answers solved 1,625/1,625 targets with an average of 3.387 guesses and a worst case of 6 guesses.

## Notes

The notebook remains in the repo as the original prototype. The maintained implementation is the Python package.
