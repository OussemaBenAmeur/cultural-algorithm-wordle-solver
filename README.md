# Cultural Algorithm Wordle Solver

This project applies a cultural algorithm to the Wordle problem in the context of an academic Algorithms and Data Structures project.

Wordle can be viewed as a constrained search problem: after each guess, the feedback narrows the set of valid solutions. This repository explores that search process through a cultural algorithm, where a population of candidate guesses evolves under the influence of a shared belief space built from accumulated knowledge.

`crate ⬛🟨⬛⬛🟩 -> carol 🟩🟨⬛⬛⬛ -> cigar 🟩🟩🟩🟩🟩`

## Objective

The goal is to study how ideas from evolutionary computation can be used to solve Wordle efficiently while keeping the implementation grounded in classic algorithmic concerns such as filtering, scoring, candidate reduction, and search strategy.

## Cultural Algorithm Perspective

The solver is organized around the main elements of a cultural algorithm:

- `Population space`: candidate guesses explored at each generation
- `Belief space`: shared knowledge extracted from feasible answers and accepted individuals
- `Acceptance`: selection of strong individuals that are allowed to update the belief space
- `Influence`: use of the belief space to guide the next generation of guesses

Wordle feedback is represented with the usual tile states:

- `🟩` correct letter in the correct position
- `🟨` correct letter in the wrong position
- `⬛` letter absent under Wordle’s duplicate-letter rules

## Repository Structure

- `cultural_wordle/`: solver implementation and command-line entry point
- `tests/`: rule and solver verification
- `short-list-of-words.txt`: answer list
- `long-list-of-words.txt`: allowed guess list
- `worlde-solver.ipynb`: original notebook prototype

## Run

```bash
python3 -m cultural_wordle --answer jazzy
```

## Test

```bash
python3 -m unittest -v
```
