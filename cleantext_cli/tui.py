"""Interactive TUI dashboard for CleanText-CLI.

Provides a terminal-based interactive dashboard using only ANSI escape
codes (no external dependencies). Displays score gauges, detection lists,
fix suggestions, and file statistics.
"""

import os
import sys
import termios
import tty
from typing import List, Optional

from cleantext_cli.detector import Detection, DetectionResult
from cleantext_cli.scorer import ScoreReport
from cleantext_cli.fixer import FixSuggestion
from cleantext_cli.reporter import Colors, _supports_color


# ---------------------------------------------------------------------------
# Terminal utilities
# ---------------------------------------------------------------------------

def _get_terminal_size() -> tuple:
    """Get the terminal window size.

    Returns:
        Tuple of (rows, columns). Defaults to (24, 80) if unavailable.
    """
    try:
        rows, cols = os.get_terminal_size()
        return rows, cols
    except OSError:
        return 24, 80


def _clear_screen():
    """Clear the terminal screen and move cursor to top-left."""
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def _hide_cursor():
    """Hide the terminal cursor."""
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()


def _show_cursor():
    """Show the terminal cursor."""
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()


def _move_cursor(row: int, col: int):
    """Move the terminal cursor to the specified position.

    Args:
        row: Row number (1-based).
        col: Column number (1-based).
    """
    sys.stdout.write(f"\033[{row};{col}H")
    sys.stdout.flush()


def _read_key() -> str:
    """Read a single keypress from the terminal.

    Returns:
        The key character or special key name.
    """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == '\x1b':  # Escape sequence
            ch2 = sys.stdin.read(1)
            if ch2 == '[':
                ch3 = sys.stdin.read(1)
                if ch3 == 'A':
                    return 'UP'
                elif ch3 == 'B':
                    return 'DOWN'
                elif ch3 == 'C':
                    return 'RIGHT'
                elif ch3 == 'D':
                    return 'LEFT'
                elif ch3 == '5':
                    sys.stdin.read(1)  # Consume '~'
                    return 'PAGE_UP'
                elif ch3 == '6':
                    sys.stdin.read(1)  # Consume '~'
                    return 'PAGE_DOWN'
                return f'ESC[{ch3}'
            return f'ESC'
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def _truncate(text: str, max_len: int) -> str:
    """Truncate text to fit within a maximum length.

    Args:
        text: The text to truncate.
        max_len: Maximum length in characters.

    Returns:
        Truncated text with '...' suffix if needed.
    """
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."


# ---------------------------------------------------------------------------
# Visual components
# ---------------------------------------------------------------------------

def _draw_gauge(score: float, label: str, row: int, col: int, width: int = 30):
    """Draw a horizontal score gauge at the specified position.

    Args:
        score: Score from 1 to 10.
        label: Label text for the gauge.
        row: Terminal row position (1-based).
        col: Terminal column position (1-based).
        width: Width of the gauge bar in characters.
    """
    _move_cursor(row, col)

    # Label
    label_text = f"{label:<12}"
    sys.stdout.write(label_text)

    # Score value
    if score >= 8.0:
        color = Colors.GREEN
    elif score >= 6.0:
        color = Colors.YELLOW
    elif score >= 4.0:
        color = Colors.MAGENTA
    else:
        color = Colors.RED

    score_text = f"{score:.1f}/10"
    sys.stdout.write(f"{Colors.BOLD}{color}{score_text}{Colors.RESET} ")

    # Bar
    filled = int(score / 10 * width)
    empty = width - filled
    bar_color = color if _supports_color() else ""
    sys.stdout.write(f"[{bar_color}{'#' * filled}{Colors.GRAY}{'-' * empty}{Colors.RESET}]")

    sys.stdout.flush()


def _draw_box(
    title: str,
    content_lines: List[str],
    row: int,
    col: int,
    width: int,
    height: int,
    selected_idx: int = -1,
):
    """Draw a bordered box with title and content.

    Args:
        title: Box title text.
        content_lines: List of content lines to display.
        row: Terminal row position (1-based).
        col: Terminal column position (1-based).
        width: Box width in characters.
        height: Box height in characters (including borders).
        selected_idx: Index of the selected/highlighted line (-1 for none).
    """
    inner_width = width - 2  # Subtract left and right borders

    # Top border
    _move_cursor(row, col)
    sys.stdout.write(f"{Colors.BLUE}+{'-' * inner_width}+{Colors.RESET}")

    # Title bar
    _move_cursor(row + 1, col)
    title_display = _truncate(title, inner_width - 4)
    sys.stdout.write(
        f"{Colors.BLUE}|{Colors.BOLD} {title_display} "
        f"{' ' * (inner_width - len(title_display) - 2)}"
        f"{Colors.BLUE}|{Colors.RESET}"
    )

    # Separator
    _move_cursor(row + 2, col)
    sys.stdout.write(f"{Colors.BLUE}+{'-' * inner_width}+{Colors.RESET}")

    # Content lines
    content_height = height - 4  # Top border, title, separator, bottom border
    for i in range(content_height):
        _move_cursor(row + 3 + i, col)
        if i < len(content_lines):
            line = content_lines[i]
            if i == selected_idx:
                sys.stdout.write(
                    f"{Colors.BLUE}|{Colors.WHITE}{Colors.BOLD}{'>'} "
                    f"{_truncate(line, inner_width - 3)}"
                    f"{' ' * max(0, inner_width - len(line) - 3)}"
                    f"{Colors.BLUE}|{Colors.RESET}"
                )
            else:
                sys.stdout.write(
                    f"{Colors.BLUE}| {_truncate(line, inner_width - 3)}"
                    f"{' ' * max(0, inner_width - len(line) - 3)}"
                    f"{Colors.BLUE}|{Colors.RESET}"
                )
        else:
            sys.stdout.write(
                f"{Colors.BLUE}|{' ' * inner_width}|{Colors.RESET}"
            )

    # Bottom border
    _move_cursor(row + 3 + content_height, col)
    sys.stdout.write(f"{Colors.BLUE}+{'-' * inner_width}+{Colors.RESET}")

    sys.stdout.flush()


# ---------------------------------------------------------------------------
# TUI Dashboard
# ---------------------------------------------------------------------------

class TUI:
    """Interactive TUI dashboard for CleanText-CLI.

    Displays analysis results in an interactive terminal interface with:
    - Score gauges for each dimension
    - Scrollable detection list
    - Fix suggestions panel
    - File statistics summary

    Navigation:
        UP/DOWN: Scroll through detections
        q/ESC: Exit
        r: Refresh
    """

    def __init__(
        self,
        result: DetectionResult,
        score_report: ScoreReport,
        text: str,
        filename: str = "",
        suggestions: Optional[List[FixSuggestion]] = None,
    ):
        """Initialize the TUI dashboard.

        Args:
            result: DetectionResult from the detector.
            score_report: ScoreReport from the scorer.
            text: The original analyzed text.
            filename: Name of the analyzed file.
            suggestions: List of fix suggestions.
        """
        self.result = result
        self.score_report = score_report
        self.text = text
        self.filename = filename
        self.suggestions = suggestions or []

        self.scroll_offset = 0
        self.selected_idx = 0
        self.running = True

        self.rows, self.cols = _get_terminal_size()

    def _build_detection_lines(self) -> List[str]:
        """Build display lines for the detection list.

        Returns:
            List of formatted detection strings.
        """
        lines = []
        for d in self.result.detections:
            sev_icon = {"error": "[E]", "warning": "[W]", "info": "[I]"}.get(
                d.severity, "[?]"
            )
            desc = d.description or d.text
            line = f"{sev_icon} L{d.line}:C{d.col} {desc}"
            if d.replacement:
                line += f" -> {d.replacement}"
            lines.append(line)

        if not lines:
            lines.append("No detections found. Text looks natural!")

        return lines

    def _build_suggestion_lines(self) -> List[str]:
        """Build display lines for the fix suggestions panel.

        Returns:
            List of formatted suggestion strings.
        """
        lines = []
        for i, s in enumerate(self.suggestions, 1):
            line = f"{i}. {s.reason}"
            if s.replacement:
                line += f" [{s.confidence}]"
            lines.append(line)

        if not lines:
            lines.append("No fix suggestions available.")

        return lines

    def _build_stats_lines(self) -> List[str]:
        """Build display lines for the statistics panel.

        Returns:
            List of formatted statistic strings.
        """
        return [
            f"File:        {self.filename or '(stdin)'}",
            f"Language:    {self.result.language}",
            f"Lines:       {self.result.total_lines}",
            f"Characters:  {self.result.total_chars}",
            f"Detections:  {len(self.result.detections)}",
            f"  Errors:    {self.score_report.severity_counts.get('error', 0)}",
            f"  Warnings:  {self.score_report.severity_counts.get('warning', 0)}",
            f"  Info:      {self.score_report.severity_counts.get('info', 0)}",
            f"Grade:       {self.score_report.grade}",
            f"Fixes:       {len(self.suggestions)}",
        ]

    def _render(self):
        """Render the complete TUI dashboard."""
        _clear_screen()

        # Header
        title = f" CleanText-CLI Dashboard "
        if self.filename:
            title += f"| {self.filename} "
        _move_cursor(1, 1)
        sys.stdout.write(
            f"{Colors.BOLD}{Colors.CYAN}{title}{'=' * max(0, self.cols - len(title) - 1)}"
            f"{Colors.RESET}"
        )

        # Score gauges (row 3-7)
        gauge_row = 3
        gauge_col = 2
        _draw_gauge(self.score_report.overall, "Overall", gauge_row, gauge_col)

        for i, dim in enumerate(self.score_report.dimensions):
            _draw_gauge(dim.score, dim.name.capitalize(), gauge_row + 1 + i, gauge_col)

        # Panels
        panel_top = 10
        panel_width = self.cols - 4
        left_width = max(20, panel_width // 2 - 1)
        right_width = panel_width - left_width - 1
        panel_height = self.rows - panel_top - 4

        # Left panel: Detections
        detection_lines = self._build_detection_lines()
        visible_start = self.scroll_offset
        visible_end = min(
            visible_start + panel_height - 4,
            len(detection_lines),
        )
        visible_lines = detection_lines[visible_start:visible_end]

        selected_display = self.selected_idx - visible_start
        if selected_display < 0 or selected_display >= panel_height - 4:
            selected_display = -1

        _draw_box(
            f"Detections ({len(detection_lines)})",
            visible_lines,
            panel_top,
            1,
            left_width,
            panel_height,
            selected_idx=selected_display,
        )

        # Right panel: Suggestions + Stats
        right_col = 2 + left_width + 1
        right_height = max(6, panel_height // 2 - 1)

        suggestion_lines = self._build_suggestion_lines()
        _draw_box(
            f"Fix Suggestions ({len(self.suggestions)})",
            suggestion_lines[:right_height - 4],
            panel_top,
            right_col,
            right_width,
            right_height,
        )

        # Stats panel
        stats_lines = self._build_stats_lines()
        stats_top = panel_top + right_height + 1
        stats_height = self.rows - stats_top - 3
        _draw_box(
            "Statistics",
            stats_lines,
            stats_top,
            right_col,
            right_width,
            stats_height,
        )

        # Footer / help bar
        help_row = self.rows - 1
        _move_cursor(help_row, 1)
        sys.stdout.write(
            f"{Colors.DIM}"
            f" [UP/DOWN] Scroll  [q/ESC] Quit  "
            f"{' ' * max(0, self.cols - 40)}"
            f"{Colors.RESET}"
        )

        sys.stdout.flush()

    def _handle_input(self):
        """Handle a single keypress input.

        Updates scroll position and selection based on user input.
        """
        try:
            key = _read_key()
        except (EOFError, KeyboardInterrupt):
            self.running = False
            return

        if key in ('q', 'Q', '\x03'):  # q, Q, Ctrl+C
            self.running = False
        elif key == '\x1b' or key == 'ESC':
            self.running = False
        elif key == 'UP':
            if self.scroll_offset > 0:
                self.scroll_offset -= 1
                self.selected_idx = max(0, self.selected_idx - 1)
        elif key == 'DOWN':
            detection_lines = self._build_detection_lines()
            max_scroll = max(0, len(detection_lines) - 10)
            if self.scroll_offset < max_scroll:
                self.scroll_offset += 1
                self.selected_idx = min(len(detection_lines) - 1, self.selected_idx + 1)
        elif key == 'PAGE_UP':
            self.scroll_offset = max(0, self.scroll_offset - 10)
            self.selected_idx = max(0, self.selected_idx - 10)
        elif key == 'PAGE_DOWN':
            detection_lines = self._build_detection_lines()
            max_scroll = max(0, len(detection_lines) - 10)
            self.scroll_offset = min(max_scroll, self.scroll_offset + 10)
            self.selected_idx = min(len(detection_lines) - 1, self.selected_idx + 10)

    def run(self):
        """Run the TUI dashboard main loop.

        Displays the interactive dashboard and handles user input
        until the user quits.
        """
        # Check if stdin is a tty (required for interactive mode)
        if not sys.stdin.isatty():
            print("Error: TUI mode requires an interactive terminal.", file=sys.stderr)
            print("Use 'cleantext analyze <file>' instead.", file=sys.stderr)
            sys.exit(1)

        _hide_cursor()

        try:
            while self.running:
                self._render()
                self._handle_input()
        finally:
            _show_cursor()
            _clear_screen()
            print("CleanText-CLI Dashboard closed.")
