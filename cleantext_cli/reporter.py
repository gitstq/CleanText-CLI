"""Output formatter for CleanText-CLI analysis reports.

Supports multiple output formats:
- Terminal: Colored output using ANSI escape codes (no external deps).
- JSON: Structured report data.
- HTML: Styled report with embedded CSS.
- Markdown: Formatted markdown report.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

from cleantext_cli.detector import Detection, DetectionResult
from cleantext_cli.scorer import ScoreReport
from cleantext_cli.fixer import FixSuggestion


# ---------------------------------------------------------------------------
# ANSI color codes for terminal output
# ---------------------------------------------------------------------------

class Colors:
    """ANSI color code constants for terminal output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    GRAY = "\033[90m"

    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


def _supports_color() -> bool:
    """Check if the terminal supports ANSI color output.

    Returns:
        True if the terminal supports colors.
    """
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("TERM") == "dumb":
        return False
    if not sys.stdout.isatty():
        return False
    return True


def _colorize(text: str, color: str, use_color: bool = True) -> str:
    """Wrap text in ANSI color codes.

    Args:
        text: The text to colorize.
        color: ANSI color code.
        use_color: Whether to apply color (respects NO_COLOR env var).

    Returns:
        Colorized text string, or plain text if color is disabled.
    """
    if use_color and _supports_color():
        return f"{color}{text}{Colors.RESET}"
    return text


def _severity_color(severity: str, use_color: bool = True) -> str:
    """Get the ANSI color for a severity level.

    Args:
        severity: Severity level ('info', 'warning', 'error').
        use_color: Whether to apply color.

    Returns:
        ANSI color code string.
    """
    color_map = {
        "info": Colors.CYAN,
        "warning": Colors.YELLOW,
        "error": Colors.RED,
    }
    return color_map.get(severity, Colors.WHITE)


def _score_color(score: float, use_color: bool = True) -> str:
    """Get the ANSI color for a score value.

    Args:
        score: Score from 1 to 10.
        use_color: Whether to apply color.

    Returns:
        ANSI color code string.
    """
    if score >= 8.0:
        return Colors.GREEN
    elif score >= 6.0:
        return Colors.YELLOW
    elif score >= 4.0:
        return Colors.MAGENTA
    else:
        return Colors.RED


def _grade_color(grade: str, use_color: bool = True) -> str:
    """Get the ANSI color for a letter grade.

    Args:
        grade: Letter grade (A+ through F).
        use_color: Whether to apply color.

    Returns:
        ANSI color code string.
    """
    if grade.startswith("A"):
        return Colors.GREEN
    elif grade.startswith("B"):
        return Colors.CYAN
    elif grade.startswith("C"):
        return Colors.YELLOW
    elif grade == "D":
        return Colors.MAGENTA
    else:
        return Colors.RED


def _build_score_bar(score: float, width: int = 20, use_color: bool = True) -> str:
    """Build a visual score bar for terminal output.

    Args:
        score: Score from 1 to 10.
        width: Width of the bar in characters.
        use_color: Whether to apply color.

    Returns:
        String representation of the score bar.
    """
    filled = int(score / 10 * width)
    empty = width - filled

    if score >= 8.0:
        bar_char = "="
        color = Colors.GREEN
    elif score >= 6.0:
        bar_char = "="
        color = Colors.YELLOW
    elif score >= 4.0:
        bar_char = "-"
        color = Colors.MAGENTA
    else:
        bar_char = "-"
        color = Colors.RED

    if use_color and _supports_color():
        bar = f"{color}{bar_char * filled}{Colors.GRAY}{' ' * empty}{Colors.RESET}"
    else:
        bar = f"{bar_char * filled}{' ' * empty}"

    return f"[{bar}] {score:.1f}/10"


class Reporter:
    """Report formatter for CleanText-CLI analysis results.

    Supports terminal, JSON, HTML, and Markdown output formats.

    Attributes:
        format: Output format ('terminal', 'json', 'html', 'markdown').
        no_color: Whether to disable colored output.
    """

    def __init__(self, fmt: str = "terminal", no_color: bool = False):
        """Initialize the reporter.

        Args:
            fmt: Output format. One of 'terminal', 'json', 'html', 'markdown'.
            no_color: If True, disable ANSI color codes in terminal output.
        """
        self.format = fmt
        self.no_color = no_color

    def _use_color(self) -> bool:
        """Check if color should be used for output.

        Returns:
            True if color should be applied.
        """
        return not self.no_color and _supports_color()

    def format_report(
        self,
        result: DetectionResult,
        score_report: ScoreReport,
        text: str,
        filename: str = "",
        suggestions: Optional[List[FixSuggestion]] = None,
    ) -> str:
        """Format a complete analysis report.

        Args:
            result: DetectionResult from the detector.
            score_report: ScoreReport from the scorer.
            text: The original analyzed text.
            filename: Name of the analyzed file (optional).
            suggestions: List of fix suggestions (optional).

        Returns:
            Formatted report string.
        """
        if self.format == "terminal":
            return self._format_terminal(result, score_report, text, filename, suggestions)
        elif self.format == "json":
            return self._format_json(result, score_report, text, filename, suggestions)
        elif self.format == "html":
            return self._format_html(result, score_report, text, filename, suggestions)
        elif self.format == "markdown":
            return self._format_markdown(result, score_report, text, filename, suggestions)
        else:
            raise ValueError(f"Unsupported format: {self.format}")

    # ------------------------------------------------------------------
    # Terminal format
    # ------------------------------------------------------------------

    def _format_terminal(
        self,
        result: DetectionResult,
        score_report: ScoreReport,
        text: str,
        filename: str,
        suggestions: Optional[List[FixSuggestion]],
    ) -> str:
        """Format report for terminal output with ANSI colors.

        Args:
            result: DetectionResult from the detector.
            score_report: ScoreReport from the scorer.
            text: The original text.
            filename: Filename of the analyzed file.
            suggestions: Fix suggestions.

        Returns:
            Formatted terminal string.
        """
        uc = self._use_color()
        lines = []
        lines.append("")

        # Header
        if filename:
            header = f"  CleanText Analysis: {_colorize(filename, Colors.BOLD + Colors.WHITE, uc)}"
        else:
            header = f"  CleanText Analysis"
        lines.append(header)
        lines.append(f"  {'=' * 60}")
        lines.append("")

        # Overall score
        grade_str = _colorize(
            score_report.grade, _grade_color(score_report.grade, uc) + Colors.BOLD, uc
        )
        score_bar = _build_score_bar(score_report.overall, use_color=uc)
        lines.append(f"  Overall Score: {grade_str}  {score_bar}")
        lines.append("")

        # Dimension breakdown
        lines.append(f"  {_colorize('Dimension Breakdown:', Colors.BOLD, uc)}")
        for dim in score_report.dimensions:
            bar = _build_score_bar(dim.score, width=15, use_color=uc)
            name = _colorize(f"{dim.name.capitalize():<16}", Colors.WHITE, uc)
            lines.append(f"    {name} {bar}")
            if dim.details:
                lines.append(f"      {_colorize(dim.details, Colors.GRAY, uc)}")
        lines.append("")

        # Summary stats
        lines.append(f"  {_colorize('Summary:', Colors.BOLD, uc)}")
        lines.append(f"    Detections: {score_report.detection_count}")
        lines.append(f"    Errors:     {_colorize(str(score_report.severity_counts.get('error', 0)), Colors.RED, uc)}")
        lines.append(f"    Warnings:   {_colorize(str(score_report.severity_counts.get('warning', 0)), Colors.YELLOW, uc)}")
        lines.append(f"    Info:       {_colorize(str(score_report.severity_counts.get('info', 0)), Colors.CYAN, uc)}")
        lines.append(f"    Language:   {result.language}")
        lines.append(f"    Lines:      {result.total_lines}")
        lines.append(f"    Characters: {result.total_chars}")
        lines.append("")

        # Detections
        if result.detections:
            lines.append(f"  {_colorize('Detections:', Colors.BOLD, uc)}")
            for d in result.detections[:50]:  # Limit to 50 in terminal
                sev = _colorize(
                    d.severity.upper(),
                    _severity_color(d.severity, uc) + Colors.BOLD,
                    uc,
                )
                loc = f"L{d.line}:C{d.col}"
                desc = d.description or f"'{d.text}'"
                lines.append(f"    [{sev}] {loc} {desc}")
                if d.replacement:
                    lines.append(
                        f"           {_colorize(f'-> {d.replacement}', Colors.GREEN, uc)}"
                    )
            if len(result.detections) > 50:
                remaining = len(result.detections) - 50
                lines.append(f"    ... and {remaining} more detections")
            lines.append("")
        else:
            lines.append(
                f"  {_colorize('No AI text patterns detected. Text looks natural!', Colors.GREEN + Colors.BOLD, uc)}"
            )
            lines.append("")

        # Fix suggestions
        if suggestions:
            lines.append(f"  {_colorize('Fix Suggestions:', Colors.BOLD, uc)}")
            for i, s in enumerate(suggestions[:20], 1):
                conf = _colorize(f"[{s.confidence}]", Colors.DIM, uc)
                lines.append(f"    {i}. {s.reason}")
                if s.replacement:
                    orig_str = '"' + s.original + '"'
                    repl_str = '"' + s.replacement + '"'
                    lines.append(
                        f"       {_colorize(orig_str, Colors.RED, uc)} "
                        f"-> {_colorize(repl_str, Colors.GREEN, uc)} {conf}"
                    )
            if len(suggestions) > 20:
                remaining = len(suggestions) - 20
                lines.append(f"    ... and {remaining} more suggestions")
            lines.append("")

        lines.append(f"  {'=' * 60}")
        lines.append(
            f"  Generated by CleanText-CLI v1.0.0 | "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        lines.append("")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # JSON format
    # ------------------------------------------------------------------

    def _format_json(
        self,
        result: DetectionResult,
        score_report: ScoreReport,
        text: str,
        filename: str,
        suggestions: Optional[List[FixSuggestion]],
    ) -> str:
        """Format report as structured JSON.

        Args:
            result: DetectionResult from the detector.
            score_report: ScoreReport from the scorer.
            text: The original text.
            filename: Filename of the analyzed file.
            suggestions: Fix suggestions.

        Returns:
            JSON string.
        """
        report = {
            "tool": "CleanText-CLI",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "filename": filename,
            "language": result.language,
            "stats": {
                "total_lines": result.total_lines,
                "total_chars": result.total_chars,
                "detection_count": score_report.detection_count,
            },
            "score": {
                "overall": score_report.overall,
                "grade": score_report.grade,
                "dimensions": [
                    {
                        "name": d.name,
                        "score": d.score,
                        "weight": d.weight,
                        "details": d.details,
                    }
                    for d in score_report.dimensions
                ],
            },
            "severity_counts": score_report.severity_counts,
            "detections": [
                {
                    "text": d.text,
                    "category": d.category,
                    "severity": d.severity,
                    "line": d.line,
                    "col": d.col,
                    "length": d.length,
                    "replacement": d.replacement,
                    "description": d.description,
                }
                for d in result.detections
            ],
            "suggestions": [
                s.to_dict() for s in (suggestions or [])
            ],
        }

        return json.dumps(report, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------
    # HTML format
    # ------------------------------------------------------------------

    def _format_html(
        self,
        result: DetectionResult,
        score_report: ScoreReport,
        text: str,
        filename: str,
        suggestions: Optional[List[FixSuggestion]],
    ) -> str:
        """Format report as a styled HTML document.

        Args:
            result: DetectionResult from the detector.
            score_report: ScoreReport from the scorer.
            text: The original text.
            filename: Filename of the analyzed file.
            suggestions: Fix suggestions.

        Returns:
            HTML string with embedded CSS.
        """
        # Determine score color class
        if score_report.overall >= 8.0:
            score_class = "score-good"
        elif score_report.overall >= 6.0:
            score_class = "score-ok"
        elif score_report.overall >= 4.0:
            score_class = "score-bad"
        else:
            score_class = "score-terrible"

        # Build detections HTML
        detections_html = ""
        for d in result.detections:
            sev_class = f"sev-{d.severity}"
            replacement_html = ""
            if d.replacement:
                replacement_html = (
                    f'<span class="replacement">&rarr; {d.replacement}</span>'
                )
            detections_html += f"""
            <tr class="{sev_class}">
                <td class="severity">{d.severity.upper()}</td>
                <td class="location">L{d.line}:C{d.col}</td>
                <td class="text">{d.text}</td>
                <td class="description">{d.description or ''}</td>
                <td>{replacement_html}</td>
            </tr>"""

        # Build dimension bars HTML
        dims_html = ""
        for dim in score_report.dimensions:
            pct = dim.score * 10
            dims_html += f"""
            <div class="dimension">
                <div class="dim-header">
                    <span class="dim-name">{dim.name.capitalize()}</span>
                    <span class="dim-score">{dim.score:.1f}/10</span>
                </div>
                <div class="dim-bar">
                    <div class="dim-fill" style="width: {pct}%"></div>
                </div>
                <div class="dim-details">{dim.details}</div>
            </div>"""

        # Build suggestions HTML
        suggestions_html = ""
        if suggestions:
            for i, s in enumerate(suggestions, 1):
                conf_class = f"conf-{s.confidence}"
                replacement_html = ""
                if s.replacement:
                    replacement_html = (
                        f'<span class="sug-replacement">&rarr; "{s.replacement}"</span>'
                    )
                suggestions_html += f"""
            <div class="suggestion {conf_class}">
                <span class="sug-num">{i}.</span>
                <span class="sug-reason">{s.reason}</span>
                <span class="sug-original">"{s.original}"</span>
                {replacement_html}
            </div>"""

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CleanText Analysis Report{f' - {filename}' if filename else ''}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0d1117;
            color: #c9d1d9;
            line-height: 1.6;
            padding: 2rem;
        }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        h1 {{
            font-size: 1.5rem;
            color: #58a6ff;
            margin-bottom: 0.5rem;
        }}
        .subtitle {{
            color: #8b949e;
            font-size: 0.85rem;
            margin-bottom: 2rem;
        }}
        .score-card {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            text-align: center;
        }}
        .score-value {{
            font-size: 3rem;
            font-weight: bold;
        }}
        .score-good {{ color: #3fb950; }}
        .score-ok {{ color: #d29922; }}
        .score-bad {{ color: #bc8cff; }}
        .score-terrible {{ color: #f85149; }}
        .grade {{
            font-size: 1.5rem;
            margin-left: 1rem;
        }}
        .score-bar {{
            width: 100%;
            height: 8px;
            background: #21262d;
            border-radius: 4px;
            margin-top: 1rem;
            overflow: hidden;
        }}
        .score-fill {{
            height: 100%;
            border-radius: 4px;
            transition: width 0.3s;
        }}
        .score-good .score-fill {{ background: #3fb950; }}
        .score-ok .score-fill {{ background: #d29922; }}
        .score-bad .score-fill {{ background: #bc8cff; }}
        .score-terrible .score-fill {{ background: #f85149; }}
        .section {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }}
        .section h2 {{
            font-size: 1.1rem;
            color: #58a6ff;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid #21262d;
        }}
        .dimension {{
            margin-bottom: 1rem;
        }}
        .dim-header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.3rem;
        }}
        .dim-name {{ color: #c9d1d9; font-weight: 500; }}
        .dim-score {{ color: #8b949e; font-size: 0.85rem; }}
        .dim-bar {{
            width: 100%;
            height: 6px;
            background: #21262d;
            border-radius: 3px;
            overflow: hidden;
        }}
        .dim-fill {{
            height: 100%;
            background: #58a6ff;
            border-radius: 3px;
        }}
        .dim-details {{
            color: #8b949e;
            font-size: 0.8rem;
            margin-top: 0.2rem;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 1rem;
        }}
        .stat-item {{
            text-align: center;
            padding: 0.5rem;
        }}
        .stat-value {{
            font-size: 1.5rem;
            font-weight: bold;
            color: #58a6ff;
        }}
        .stat-label {{
            font-size: 0.8rem;
            color: #8b949e;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
        }}
        th {{
            text-align: left;
            padding: 0.5rem;
            color: #8b949e;
            border-bottom: 1px solid #21262d;
            font-weight: 500;
        }}
        td {{
            padding: 0.5rem;
            border-bottom: 1px solid #21262d;
        }}
        .sev-error .severity {{ color: #f85149; font-weight: bold; }}
        .sev-warning .severity {{ color: #d29922; font-weight: bold; }}
        .sev-info .severity {{ color: #58a6ff; }}
        .replacement {{ color: #3fb950; font-size: 0.8rem; }}
        .suggestion {{
            padding: 0.5rem 0;
            border-bottom: 1px solid #21262d;
            font-size: 0.85rem;
        }}
        .sug-num {{ color: #8b949e; margin-right: 0.5rem; }}
        .sug-reason {{ color: #c9d1d9; }}
        .sug-original {{ color: #f85149; margin: 0 0.3rem; }}
        .sug-replacement {{ color: #3fb950; }}
        .conf-high {{ border-left: 3px solid #3fb950; padding-left: 0.5rem; }}
        .conf-medium {{ border-left: 3px solid #d29922; padding-left: 0.5rem; }}
        .conf-low {{ border-left: 3px solid #8b949e; padding-left: 0.5rem; }}
        .footer {{
            text-align: center;
            color: #484f58;
            font-size: 0.8rem;
            margin-top: 2rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>CleanText Analysis Report{f' - {filename}' if filename else ''}</h1>
        <div class="subtitle">
            Generated by CleanText-CLI v1.0.0 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>

        <div class="score-card {score_class}">
            <div>
                <span class="score-value">{score_report.overall:.1f}</span>
                <span class="grade">/ 10 ({score_report.grade})</span>
            </div>
            <div class="score-bar">
                <div class="score-fill" style="width: {score_report.overall * 10}%"></div>
            </div>
        </div>

        <div class="section">
            <h2>Dimension Breakdown</h2>
            {dims_html}
        </div>

        <div class="section">
            <h2>Summary</h2>
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-value">{score_report.detection_count}</div>
                    <div class="stat-label">Detections</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" style="color: #f85149">{score_report.severity_counts.get('error', 0)}</div>
                    <div class="stat-label">Errors</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" style="color: #d29922">{score_report.severity_counts.get('warning', 0)}</div>
                    <div class="stat-label">Warnings</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" style="color: #58a6ff">{score_report.severity_counts.get('info', 0)}</div>
                    <div class="stat-label">Info</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{result.language}</div>
                    <div class="stat-label">Language</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{result.total_lines}</div>
                    <div class="stat-label">Lines</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>Detections ({len(result.detections)})</h2>
            <table>
                <thead>
                    <tr>
                        <th>Severity</th>
                        <th>Location</th>
                        <th>Text</th>
                        <th>Description</th>
                        <th>Fix</th>
                    </tr>
                </thead>
                <tbody>
                    {detections_html if detections_html else '<tr><td colspan="5" style="text-align:center;color:#3fb950">No AI text patterns detected.</td></tr>'}
                </tbody>
            </table>
        </div>

        {'<div class="section"><h2>Fix Suggestions</h2>' + suggestions_html + '</div>' if suggestions_html else ''}

        <div class="footer">
            CleanText-CLI v1.0.0 | AI Text Style Purification Engine
        </div>
    </div>
</body>
</html>"""
        return html

    # ------------------------------------------------------------------
    # Markdown format
    # ------------------------------------------------------------------

    def _format_markdown(
        self,
        result: DetectionResult,
        score_report: ScoreReport,
        text: str,
        filename: str,
        suggestions: Optional[List[FixSuggestion]],
    ) -> str:
        """Format report as Markdown.

        Args:
            result: DetectionResult from the detector.
            score_report: ScoreReport from the scorer.
            text: The original text.
            filename: Filename of the analyzed file.
            suggestions: Fix suggestions.

        Returns:
            Markdown formatted string.
        """
        md_lines = []

        # Header
        md_lines.append(f"# CleanText Analysis Report")
        if filename:
            md_lines.append(f"**File:** `{filename}`")
        md_lines.append(
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
            f"**Language:** {result.language}"
        )
        md_lines.append("")

        # Overall score
        md_lines.append("## Overall Score")
        md_lines.append(f"**{score_report.overall:.1f} / 10** (Grade: **{score_report.grade}**)")
        md_lines.append("")

        # Dimension breakdown
        md_lines.append("## Dimension Breakdown")
        md_lines.append("")
        md_lines.append("| Dimension | Score | Weight | Details |")
        md_lines.append("|-----------|-------|--------|---------|")
        for dim in score_report.dimensions:
            md_lines.append(
                f"| {dim.name.capitalize()} | {dim.score:.1f}/10 | {dim.weight:.0%} | {dim.details} |"
            )
        md_lines.append("")

        # Summary
        md_lines.append("## Summary")
        md_lines.append("")
        md_lines.append(f"- **Detections:** {score_report.detection_count}")
        md_lines.append(f"- **Errors:** {score_report.severity_counts.get('error', 0)}")
        md_lines.append(f"- **Warnings:** {score_report.severity_counts.get('warning', 0)}")
        md_lines.append(f"- **Info:** {score_report.severity_counts.get('info', 0)}")
        md_lines.append(f"- **Lines:** {result.total_lines}")
        md_lines.append(f"- **Characters:** {result.total_chars}")
        md_lines.append("")

        # Detections
        md_lines.append("## Detections")
        if result.detections:
            md_lines.append("")
            md_lines.append("| # | Severity | Location | Text | Description | Fix |")
            md_lines.append("|---|----------|----------|------|-------------|-----|")
            for i, d in enumerate(result.detections, 1):
                sev_icon = {"error": ":x:", "warning": ":warning:", "info": ":info:"}.get(
                    d.severity, ""
                )
                fix = d.replacement or ""
                md_lines.append(
                    f"| {i} | {sev_icon} {d.severity} | L{d.line}:C{d.col} | `{d.text}` | {d.description or ''} | {fix} |"
                )
            md_lines.append("")
        else:
            md_lines.append("")
            md_lines.append("> No AI text patterns detected. Text looks natural!")
            md_lines.append("")

        # Suggestions
        if suggestions:
            md_lines.append("## Fix Suggestions")
            md_lines.append("")
            for i, s in enumerate(suggestions, 1):
                md_lines.append(f"{i}. **{s.reason}**")
                if s.replacement:
                    md_lines.append(f"   - `{s.original}` -> `{s.replacement}` [{s.confidence}]")
                else:
                    md_lines.append(f"   - `{s.original}` -> *(delete)* [{s.confidence}]")
            md_lines.append("")

        # Footer
        md_lines.append("---")
        md_lines.append("*Generated by CleanText-CLI v1.0.0*")

        return "\n".join(md_lines)
