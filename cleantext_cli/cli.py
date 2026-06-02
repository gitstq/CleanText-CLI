"""CLI entry point for CleanText-CLI.

Provides command-line interface for analyzing, scoring, and fixing
AI-generated text patterns. Supports multiple output formats, pipe mode,
git hook installation, and interactive TUI dashboard.

Usage:
    cleantext analyze <file> [--lang auto|en|zh] [--format terminal|json|html|md]
    cleantext analyze --stdin
    cleantext fix <file>
    cleantext fix --stdin
    cleantext score <file>
    cleantext hook install
    cleantext tui
"""

import argparse
import os
import sys
from typing import Optional

from cleantext_cli import __version__
from cleantext_cli.detector import Detector
from cleantext_cli.scorer import Scorer
from cleantext_cli.fixer import Fixer
from cleantext_cli.reporter import Reporter


# ---------------------------------------------------------------------------
# Git pre-commit hook script
# ---------------------------------------------------------------------------

GIT_HOOK_SCRIPT = """\
#!/usr/bin/env python3
# CleanText-CLI git pre-commit hook.
# Checks staged .md, .txt, and .rst files for AI-generated text patterns.
# Blocks the commit if the overall score is below the threshold.

import os
import subprocess
import sys


def get_staged_files():
    \"\"\"Get list of staged files that match our target extensions.\"\"\"
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM",
             "--", "*.md", "*.txt", "*.rst"],
            capture_output=True, text=True, check=True,
        )
        return [f.strip() for f in result.stdout.strip().split("\\n") if f.strip()]
    except subprocess.CalledProcessError:
        return []


def main():
    threshold = float(os.environ.get("CLEANTEXT_THRESHOLD", "5.0"))
    staged = get_staged_files()

    if not staged:
        return 0

    # Try to import cleantext_cli
    try:
        from cleantext_cli.detector import Detector
        from cleantext_cli.scorer import Scorer
    except ImportError:
        print("CleanText-CLI not installed. Skipping pre-commit check.", file=sys.stderr)
        return 0

    has_issues = False
    for filepath in staged:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
        except (IOError, OSError) as e:
            print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)
            continue

        if not text.strip():
            continue

        detector = Detector(lang="auto", min_severity="warning")
        scorer = Scorer()
        result = detector.analyze(text)
        report = scorer.score(result, text)

        if report.overall < threshold:
            print(f"CleanText: {filepath} score {report.overall:.1f}/10 "
                  f"(grade {report.grade}) -- below threshold {threshold}",
                  file=sys.stderr)
            has_issues = True
        else:
            print(f"CleanText: {filepath} score {report.overall:.1f}/10 "
                  f"(grade {report.grade}) -- OK")

    if has_issues:
        print("\\nCleanText-CLI: Some files have low scores. "
              "Commit blocked. Fix or set CLEANTEXT_THRESHOLD.",
              file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
"""


def _read_file(filepath: str) -> str:
    """Read file contents with encoding detection.

    Args:
        filepath: Path to the file to read.

    Returns:
        File contents as string.

    Raises:
        SystemExit: If the file cannot be read.
    """
    encodings = ["utf-8", "utf-8-sig", "gbk", "gb2312", "latin-1"]
    for enc in encodings:
        try:
            with open(filepath, "r", encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
        except (IOError, OSError) as e:
            print(f"Error: Cannot read file '{filepath}': {e}", file=sys.stderr)
            sys.exit(1)
    print(f"Error: Cannot decode file '{filepath}' with any known encoding.", file=sys.stderr)
    sys.exit(1)


def _read_stdin() -> str:
    """Read text from stdin (pipe mode).

    Returns:
        Text read from stdin.

    Raises:
        SystemExit: If stdin is a tty (not piped).
    """
    if sys.stdin.isatty():
        print("Error: --stdin requires piped input. Usage: echo 'text' | cleantext analyze --stdin",
              file=sys.stderr)
        sys.exit(1)
    return sys.stdin.read()


def _write_output(content: str, output_file: Optional[str] = None):
    """Write output to file or stdout.

    Args:
        content: The content to write.
        output_file: Optional file path. If None, writes to stdout.
    """
    if output_file:
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Output written to: {output_file}", file=sys.stderr)
        except (IOError, OSError) as e:
            print(f"Error: Cannot write to '{output_file}': {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(content)


def cmd_analyze(args):
    """Handle the 'analyze' command.

    Analyzes text for AI-generated patterns and outputs a full report.

    Args:
        args: Parsed command-line arguments.
    """
    # Read input
    if args.stdin:
        text = _read_stdin()
        filename = "(stdin)"
    else:
        text = _read_file(args.file)
        filename = args.file

    if not text.strip():
        print("Warning: Input text is empty.", file=sys.stderr)
        sys.exit(0)

    # Detect
    detector = Detector(lang=args.lang, min_severity=args.severity)
    result = detector.analyze(text)

    # Score
    scorer = Scorer()
    score_report = scorer.score(result, text)

    # Fix suggestions
    fixer = Fixer()
    suggestions = fixer.suggest_fixes(result)

    # Report
    reporter = Reporter(fmt=args.format, no_color=args.no_color)
    report = reporter.format_report(
        result=result,
        score_report=score_report,
        text=text,
        filename=filename,
        suggestions=suggestions,
    )

    _write_output(report, args.output)

    # Exit code: 1 if score is low (for CI usage)
    if score_report.overall < 4.0:
        sys.exit(1)


def cmd_fix(args):
    """Handle the 'fix' command.

    Automatically fixes AI text patterns and outputs cleaned text.

    Args:
        args: Parsed command-line arguments.
    """
    # Read input
    if args.stdin:
        text = _read_stdin()
        filename = "(stdin)"
    else:
        text = _read_file(args.file)
        filename = args.file

    if not text.strip():
        print("Warning: Input text is empty.", file=sys.stderr)
        sys.exit(0)

    # Detect
    detector = Detector(lang=args.lang, min_severity=args.severity)
    result = detector.analyze(text)

    # Fix
    fixer = Fixer()
    fixed_text, suggestions = fixer.auto_fix(text, result)

    # Show summary
    if suggestions:
        print(f"Applied {len(suggestions)} fixes to {filename}", file=sys.stderr)

        # Also show before/after scores
        scorer = Scorer()
        before_report = scorer.score(result, text)

        after_result = detector.analyze(fixed_text)
        after_report = scorer.score(after_result, fixed_text)

        print(
            f"Score: {before_report.overall:.1f} -> {after_report.overall:.1f} "
            f"({before_report.grade} -> {after_report.grade})",
            file=sys.stderr,
        )
    else:
        print(f"No fixes needed for {filename}", file=sys.stderr)

    _write_output(fixed_text, args.output)


def cmd_score(args):
    """Handle the 'score' command.

    Outputs only the overall score and grade.

    Args:
        args: Parsed command-line arguments.
    """
    text = _read_file(args.file)
    filename = args.file

    if not text.strip():
        print("0.0 F", file=sys.stderr)
        sys.exit(0)

    detector = Detector(lang=args.lang, min_severity="info")
    result = detector.analyze(text)

    scorer = Scorer()
    score_report = scorer.score(result, text)

    print(f"{score_report.overall:.1f} {score_report.grade}")

    sys.exit(0 if score_report.overall >= 5.0 else 1)


def cmd_hook(args):
    """Handle the 'hook install' command.

    Installs a git pre-commit hook that checks staged files.

    Args:
        args: Parsed command-line arguments.
    """
    # Find git directory
    git_dir = None
    cwd = os.getcwd()
    while cwd != os.path.dirname(cwd):
        if os.path.isdir(os.path.join(cwd, ".git")):
            git_dir = os.path.join(cwd, ".git")
            break
        if os.path.isfile(os.path.join(cwd, ".git")):
            # Submodule or worktree
            git_dir = os.path.join(cwd, ".git")
            break
        cwd = os.path.dirname(cwd)

    if not git_dir:
        print("Error: Not a git repository. Run 'git init' first.", file=sys.stderr)
        sys.exit(1)

    hooks_dir = os.path.join(git_dir, "hooks")
    if not os.path.isdir(hooks_dir):
        os.makedirs(hooks_dir)

    hook_path = os.path.join(hooks_dir, "pre-commit")

    if os.path.exists(hook_path):
        # Check if it's already our hook
        try:
            with open(hook_path, "r") as f:
                existing = f.read()
            if "CleanText-CLI" in existing:
                print("CleanText-CLI pre-commit hook is already installed.", file=sys.stderr)
                sys.exit(0)
        except (IOError, OSError):
            pass

        # Backup existing hook
        backup_path = hook_path + ".backup"
        try:
            os.rename(hook_path, backup_path)
            print(f"Backed up existing hook to: {backup_path}", file=sys.stderr)
        except OSError as e:
            print(f"Warning: Could not backup existing hook: {e}", file=sys.stderr)
            sys.exit(1)

    # Write hook
    try:
        with open(hook_path, "w") as f:
            f.write(GIT_HOOK_SCRIPT)
        os.chmod(hook_path, 0o755)
        print(f"CleanText-CLI pre-commit hook installed to: {hook_path}", file=sys.stderr)
        print("Set CLEANTEXT_THRESHOLD environment variable to adjust the minimum score (default: 5.0).",
              file=sys.stderr)
    except (IOError, OSError) as e:
        print(f"Error: Could not write hook: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_tui(args):
    """Handle the 'tui' command.

    Launches the interactive TUI dashboard.

    Args:
        args: Parsed command-line arguments.
    """
    from cleantext_cli.tui import TUI

    # Read input
    if args.stdin:
        text = _read_stdin()
        filename = "(stdin)"
    elif args.file:
        text = _read_file(args.file)
        filename = args.file
    else:
        print("Error: TUI requires a file or --stdin input.", file=sys.stderr)
        sys.exit(1)

    if not text.strip():
        print("Error: Input text is empty.", file=sys.stderr)
        sys.exit(1)

    # Detect
    detector = Detector(lang=args.lang, min_severity=args.severity)
    result = detector.analyze(text)

    # Score
    scorer = Scorer()
    score_report = scorer.score(result, text)

    # Fix suggestions
    fixer = Fixer()
    suggestions = fixer.suggest_fixes(result)

    # Launch TUI
    tui = TUI(
        result=result,
        score_report=score_report,
        text=text,
        filename=filename,
        suggestions=suggestions,
    )
    tui.run()


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for CleanText-CLI.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="cleantext",
        description="CleanText-CLI: AI text style purification engine. "
                    "Detect and clean AI-generated text patterns.",
        epilog="Examples:\n"
               "  cleantext analyze document.md\n"
               "  cleantext analyze --stdin --format json < document.md\n"
               "  cleantext fix --stdin < input.txt > output.txt\n"
               "  cleantext score document.md\n"
               "  cleantext hook install\n"
               "  cleantext tui document.md",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- analyze command ---
    analyze_parser = subparsers.add_parser(
        "analyze", help="Analyze text for AI-generated patterns"
    )
    analyze_parser.add_argument(
        "file", nargs="?", help="File to analyze (omit with --stdin)"
    )
    analyze_parser.add_argument(
        "--stdin", action="store_true",
        help="Read input from stdin (pipe mode)"
    )
    analyze_parser.add_argument(
        "--lang", choices=["auto", "en", "zh"], default="auto",
        help="Language to use for detection (default: auto)"
    )
    analyze_parser.add_argument(
        "--format", choices=["terminal", "json", "html", "markdown"], default="terminal",
        help="Output format (default: terminal)"
    )
    analyze_parser.add_argument(
        "--severity", choices=["info", "warning", "error"], default="info",
        help="Minimum severity to report (default: info)"
    )
    analyze_parser.add_argument(
        "--no-color", action="store_true",
        help="Disable colored terminal output"
    )
    analyze_parser.add_argument(
        "--output", "-o", metavar="FILE",
        help="Write output to file instead of stdout"
    )

    # --- fix command ---
    fix_parser = subparsers.add_parser(
        "fix", help="Auto-fix AI text patterns"
    )
    fix_parser.add_argument(
        "file", nargs="?", help="File to fix (omit with --stdin)"
    )
    fix_parser.add_argument(
        "--stdin", action="store_true",
        help="Read input from stdin (pipe mode)"
    )
    fix_parser.add_argument(
        "--lang", choices=["auto", "en", "zh"], default="auto",
        help="Language to use for detection (default: auto)"
    )
    fix_parser.add_argument(
        "--severity", choices=["info", "warning", "error"], default="info",
        help="Minimum severity to fix (default: info)"
    )
    fix_parser.add_argument(
        "--output", "-o", metavar="FILE",
        help="Write output to file instead of stdout"
    )

    # --- score command ---
    score_parser = subparsers.add_parser(
        "score", help="Quick score only (outputs: SCORE GRADE)"
    )
    score_parser.add_argument(
        "file", help="File to score"
    )
    score_parser.add_argument(
        "--lang", choices=["auto", "en", "zh"], default="auto",
        help="Language to use for detection (default: auto)"
    )

    # --- hook command ---
    hook_parser = subparsers.add_parser(
        "hook", help="Manage git hooks"
    )
    hook_subparsers = hook_parser.add_subparsers(dest="hook_command")
    hook_subparsers.add_parser(
        "install", help="Install git pre-commit hook"
    )

    # --- tui command ---
    tui_parser = subparsers.add_parser(
        "tui", help="Launch interactive TUI dashboard"
    )
    tui_parser.add_argument(
        "file", nargs="?", help="File to analyze in TUI"
    )
    tui_parser.add_argument(
        "--stdin", action="store_true",
        help="Read input from stdin"
    )
    tui_parser.add_argument(
        "--lang", choices=["auto", "en", "zh"], default="auto",
        help="Language to use for detection (default: auto)"
    )
    tui_parser.add_argument(
        "--severity", choices=["info", "warning", "error"], default="info",
        help="Minimum severity to report (default: info)"
    )

    return parser


def main(argv: Optional[list] = None):
    """Main entry point for CleanText-CLI.

    Parses command-line arguments and dispatches to the appropriate
    command handler.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:]).
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "analyze":
        cmd_analyze(args)
    elif args.command == "fix":
        cmd_fix(args)
    elif args.command == "score":
        cmd_score(args)
    elif args.command == "hook":
        if not hasattr(args, "hook_command") or not args.hook_command:
            parser.parse_args(["hook", "--help"])
        elif args.hook_command == "install":
            cmd_hook(args)
    elif args.command == "tui":
        cmd_tui(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
