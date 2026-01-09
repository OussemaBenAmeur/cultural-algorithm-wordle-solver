# Cultural Algorithm Wordle Solver

Using a cultural algorithm to solve Wordle - an evolutionary computation approach to efficiently guess the target word.

## 📋 About

This project implements a **Cultural Algorithm** to solve the popular word game Wordle. Cultural Algorithms are a type of evolutionary computation that models the evolution of both individual knowledge (population space) and group knowledge (belief space), making them particularly effective for optimization problems like Wordle solving.

The algorithm learns from each guess and its feedback (green, yellow, gray tiles) to progressively narrow down the possible word solutions, using cultural knowledge to guide future guesses.

## 🎯 What is a Cultural Algorithm?

A Cultural Algorithm is an evolutionary computation technique that maintains two spaces:
- **Population Space**: Represents individual solutions (potential word guesses)
- **Belief Space**: Represents shared knowledge and cultural information (learned patterns, constraints, and heuristics)

The algorithm evolves both spaces through:
1. **Acceptance Function**: Selects individuals whose experiences can influence the belief space
2. **Update Function**: Modifies the belief space based on accepted individuals
3. **Influence Function**: Uses the belief space to guide the evolution of the population space

## 🚀 Features

- **Cultural Algorithm Implementation**: Full implementation of the cultural algorithm for Wordle solving
- **Intelligent Word Selection**: Uses learned patterns and constraints to make optimal guesses
- **Feedback Integration**: Incorporates Wordle feedback (green/yellow/gray) to refine guesses
- **Multiple Word Lists**: Supports both short and long word lists for different difficulty levels
- **Visualization**: Includes video demonstration of the solver in action

## 📁 Project Structure

```
cultural-algorithm-wordle-solver/
├── worlde-solver.ipynb                    # Main solver implementation
├── short-list-of-words.txt                # Shorter word list for faster testing
├── long-list-of-words.txt                 # Comprehensive word list
├── WordleGuessScene@2025-12-08@23-16-19.mp4  # Video demonstration
├── projet_module.pdf                      # Project documentation
└── README.md                              # This file
```

## 🛠️ Technologies Used

- **Python**: Core programming language
- **Jupyter Notebooks**: Interactive development and execution environment
- **Cultural Algorithm**: Evolutionary computation technique
- **Word Lists**: Curated dictionaries for valid Wordle words

## 🎮 How It Works

1. **Initialization**: The algorithm starts with a population of potential word guesses and an empty belief space
2. **Guessing**: Makes a word guess based on current knowledge
3. **Feedback Processing**: Receives Wordle feedback:
   - 🟩 Green: Correct letter in correct position
   - 🟨 Yellow: Correct letter in wrong position
   - ⬜ Gray: Letter not in the word
4. **Knowledge Update**: Updates the belief space with constraints and patterns learned from feedback
5. **Evolution**: Uses cultural knowledge to guide the next generation of guesses
6. **Convergence**: Repeats until the target word is found

## 📊 Word Lists

- **short-list-of-words.txt**: A curated list of common words for faster testing
- **long-list-of-words.txt**: A comprehensive list of valid Wordle words

## 📚 Documentation

See `projet_module.pdf` for detailed project documentation and methodology.

## 🔬 Algorithm Advantages

- **Adaptive Learning**: Continuously learns from feedback to improve guesses
- **Cultural Knowledge**: Maintains shared knowledge that guides the search
- **Efficient Search**: Uses learned constraints to narrow the search space quickly
- **Robust**: Handles various word patterns and constraints effectively

## 📝 License

This project is open source and available for educational and research purposes.

## 📖 References

- Cultural Algorithms: A model of evolutionary computation with cultural learning
- Wordle: The popular word-guessing game by Josh Wardle

---

⭐ If you find this project useful, please consider giving it a star!
