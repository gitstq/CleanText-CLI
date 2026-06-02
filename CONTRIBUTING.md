# Contributing to CleanText-CLI

Thank you for your interest in contributing to CleanText-CLI!

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Make sure you have Python 3.7+ installed (no other dependencies needed)
4. Run the entry script directly: `python cleantext --help`

## Development Workflow

No build step is required. Simply edit the source files and test by running:

```bash
# Run directly without installing
python cleantext analyze test_file.md

# Or install in development mode
pip install -e .
cleantext analyze test_file.md
```

## Adding New Detection Rules

Detection rules are defined in:
- `cleantext_cli/rules/en.py` -- English AI text patterns
- `cleantext_cli/rules/zh.py` -- Chinese AI text patterns

Each rule is a tuple of `(pattern, category, severity, replacement)`.

### Rule Categories

- `cliche_opening` -- Cliché opening phrases
- `cliche_closing` -- Cliché closing phrases
- `cliche_metaphor` -- Overused metaphors
- `cliche_phrase` -- General cliché phrases
- `overused_word` -- Overused vocabulary
- `booster_word` -- Hype/exaggeration words
- `filler_hedge` -- Filler words and hedging
- `transition_word` -- Overused transition words
- `wordiness` -- Redundant expressions
- `binary_contrast` -- "While X, Y" structures
- `hedge` -- Hedging patterns
- `booster` -- Booster words

### Severity Levels

- `info` -- Minor issue, low confidence
- `warning` -- Moderate issue, likely AI-generated
- `error` -- Strong indicator of AI-generated text

## Code Style

- Use type hints for all function signatures
- Add docstrings to all public functions and classes
- Keep zero external dependencies
- Follow PEP 8 conventions

## Submitting Changes

1. Create a feature branch from `main`
2. Make your changes
3. Test with various inputs (English and Chinese text)
4. Submit a pull request with a clear description

## Reporting Issues

When reporting issues, please include:
- The input text that triggered the issue
- Expected vs actual behavior
- Python version and operating system
