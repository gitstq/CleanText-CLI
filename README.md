# CleanText-CLI

A lightweight terminal AI text style purification engine. Detects and cleans AI-generated text patterns in English and Chinese. Zero external dependencies.

## Features

- **Pattern Detection**: 200+ AI text pattern rules for English and Chinese
- **Multi-dimensional Scoring**: Scores text 1-10 on directness, rhythm, trustworthiness, authenticity, and density
- **Auto-Fix**: Automatically cleans AI-style text with configurable confidence
- **Multiple Output Formats**: Terminal (colored), JSON, HTML, Markdown
- **Interactive TUI**: Terminal dashboard with score gauges and detection browser
- **Git Hook**: Pre-commit hook to check staged files
- **Pipe Mode**: Works with stdin for Unix pipeline integration
- **Zero Dependencies**: Uses only Python standard library

## Installation

```bash
pip install -e .
```

Or run directly without installing:

```bash
python cleantext --help
```

## Usage

```bash
# Analyze a file
cleantext analyze document.md

# Analyze from stdin (pipe mode)
cleantext analyze --stdin < document.md

# Output as JSON
cleantext analyze document.md --format json

# Output as HTML
cleantext analyze document.md --format html -o report.html

# Auto-fix a file
cleantext fix document.md

# Auto-fix from stdin
cleantext fix --stdin < input.txt > output.txt

# Quick score
cleantext score document.md

# Install git pre-commit hook
cleantext hook install

# Interactive TUI dashboard
cleantext tui document.md
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--lang` | Language: auto, en, zh | auto |
| `--format` | Output: terminal, json, html, markdown | terminal |
| `--severity` | Min severity: info, warning, error | info |
| `--no-color` | Disable colored output | false |
| `--output, -o` | Write output to file | stdout |

## License

MIT
