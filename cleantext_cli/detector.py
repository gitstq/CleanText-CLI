"""Core detection engine for AI-generated text patterns.

Scans input text against a comprehensive set of rules to identify
cliché phrases, structural patterns, hedging, booster words, and
other markers commonly found in AI-generated text.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from cleantext_cli.rules import get_rules


@dataclass
class Detection:
    """Represents a single AI text pattern detection.

    Attributes:
        text: The matched text fragment.
        category: Category of the detection (e.g. 'cliche_opening', 'overused_word').
        severity: Severity level -- 'info', 'warning', or 'error'.
        line: Line number where the detection was found (1-based).
        col: Column number where the detection starts (1-based).
        length: Length of the matched text.
        replacement: Suggested replacement text, if available.
        description: Human-readable description of the issue.
    """
    text: str
    category: str
    severity: str
    line: int
    col: int
    length: int
    replacement: str = ""
    description: str = ""


@dataclass
class DetectionResult:
    """Aggregated result of scanning a text for AI patterns.

    Attributes:
        detections: List of individual detections found.
        total_lines: Total number of lines in the input text.
        total_chars: Total number of characters in the input text.
        language: Detected or specified language of the text.
    """
    detections: List[Detection] = field(default_factory=list)
    total_lines: int = 0
    total_chars: int = 0
    language: str = "auto"


def detect_language(text: str) -> str:
    """Detect the primary language of the given text.

    Uses a simple heuristic: count Chinese characters vs Latin characters.
    If Chinese characters exceed 30% of total non-whitespace characters,
    the text is classified as Chinese.

    Args:
        text: The input text to analyze.

    Returns:
        'zh' if Chinese is detected, 'en' otherwise.
    """
    # Remove whitespace for counting
    clean = re.sub(r'\s+', '', text)
    if not clean:
        return "en"

    # Count Chinese characters (CJK Unified Ideographs range)
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf]', clean))
    ratio = chinese_chars / len(clean) if len(clean) > 0 else 0

    return "zh" if ratio > 0.3 else "en"


class Detector:
    """AI text pattern detector.

    Scans text for cliché phrases, structural patterns, sentence starters,
    hedging, and booster words that are characteristic of AI-generated text.

    Attributes:
        lang: Language to use for detection rules ('en', 'zh', or 'auto').
        min_severity: Minimum severity level to report ('info', 'warning', 'error').
    """

    SEVERITY_LEVELS = {"info": 1, "warning": 2, "error": 3}

    def __init__(self, lang: str = "auto", min_severity: str = "info"):
        """Initialize the detector.

        Args:
            lang: Language code ('en', 'zh', 'auto'). Default 'auto' detects
                  the language from the input text.
            min_severity: Minimum severity to report. One of 'info', 'warning',
                          'error'. Default 'info' reports everything.
        """
        self.lang = lang
        self.min_severity = min_severity
        self._rules_cache: Dict[str, dict] = {}

    def _get_rules(self, lang: str) -> dict:
        """Get cached rules for the specified language.

        Args:
            lang: Language code ('en' or 'zh').

        Returns:
            Dictionary of detection rules.
        """
        if lang not in self._rules_cache:
            self._rules_cache[lang] = get_rules(lang)
        return self._rules_cache[lang]

    def _severity_pass(self, severity: str) -> bool:
        """Check if a severity level meets the minimum threshold.

        Args:
            severity: The severity level to check.

        Returns:
            True if the severity meets or exceeds the minimum threshold.
        """
        return self.SEVERITY_LEVELS.get(severity, 0) >= self.SEVERITY_LEVELS.get(
            self.min_severity, 0
        )

    def _find_in_lines(
        self, text: str, pattern: str
    ) -> List[Tuple[int, int, str]]:
        """Find all occurrences of a pattern in text, returning line/col info.

        Args:
            text: The full input text.
            pattern: The string pattern to search for (case-insensitive).

        Returns:
            List of (line_number, column_number, matched_text) tuples.
        """
        results = []
        lines = text.split('\n')
        pattern_lower = pattern.lower()

        for line_idx, line in enumerate(lines):
            line_lower = line.lower()
            search_start = 0
            while True:
                pos = line_lower.find(pattern_lower, search_start)
                if pos == -1:
                    break
                results.append((line_idx + 1, pos + 1, line[pos:pos + len(pattern)]))
                search_start = pos + 1

        return results

    def _find_regex_in_lines(
        self, text: str, regex_pattern: str
    ) -> List[Tuple[int, int, str]]:
        """Find all regex matches in text, returning line/col info.

        Args:
            text: The full input text.
            regex_pattern: The regex pattern to search with.

        Returns:
            List of (line_number, column_number, matched_text) tuples.
        """
        results = []
        lines = text.split('\n')

        for line_idx, line in enumerate(lines):
            for match in re.finditer(regex_pattern, line):
                results.append((
                    line_idx + 1,
                    match.start() + 1,
                    match.group(0),
                ))

        return results

    def _detect_cliche_phrases(
        self, text: str, rules: dict
    ) -> List[Detection]:
        """Detect cliché AI phrases in the text.

        Args:
            text: The input text.
            rules: Detection rules dictionary.

        Returns:
            List of Detection objects for found cliché phrases.
        """
        detections = []
        for phrase, category, severity, replacement in rules.get("cliche_phrases", []):
            if not self._severity_pass(severity):
                continue
            occurrences = self._find_in_lines(text, phrase)
            for line, col, matched in occurrences:
                detections.append(Detection(
                    text=matched,
                    category=category,
                    severity=severity,
                    line=line,
                    col=col,
                    length=len(matched),
                    replacement=replacement,
                    description=f"AI风格短语: '{matched}'",
                ))
        return detections

    def _detect_structural_patterns(
        self, text: str, rules: dict
    ) -> List[Detection]:
        """Detect structural cliché patterns in the text.

        Args:
            text: The input text.
            rules: Detection rules dictionary.

        Returns:
            List of Detection objects for found structural patterns.
        """
        detections = []
        for pattern, category, severity, description in rules.get(
            "structural_patterns", []
        ):
            if not self._severity_pass(severity):
                continue
            occurrences = self._find_regex_in_lines(text, pattern)
            for line, col, matched in occurrences:
                detections.append(Detection(
                    text=matched,
                    category=category,
                    severity=severity,
                    line=line,
                    col=col,
                    length=len(matched),
                    description=description,
                ))
        return detections

    def _detect_sentence_starters(
        self, text: str, rules: dict
    ) -> List[Detection]:
        """Detect overused sentence-starting patterns.

        Args:
            text: The input text.
            rules: Detection rules dictionary.

        Returns:
            List of Detection objects for found sentence starters.
        """
        detections = []
        lines = text.split('\n')

        for line_idx, line in enumerate(lines):
            stripped = line.lstrip()
            if not stripped:
                continue

            for starter, category, severity in rules.get("sentence_starters", []):
                if not self._severity_pass(severity):
                    continue
                if stripped.lower().startswith(starter.lower()):
                    # Calculate column offset for leading whitespace
                    col = len(line) - len(stripped) + 1
                    detections.append(Detection(
                        text=starter,
                        category=category,
                        severity=severity,
                        line=line_idx + 1,
                        col=col,
                        length=len(starter),
                        description=f"AI风格句首: '{starter}...'",
                    ))
                    break  # Only report one starter per line

        return detections

    def _detect_hedge_patterns(
        self, text: str, rules: dict
    ) -> List[Detection]:
        """Detect excessive hedging patterns.

        Args:
            text: The input text.
            rules: Detection rules dictionary.

        Returns:
            List of Detection objects for found hedge patterns.
        """
        detections = []
        for pattern, category, severity in rules.get("hedge_patterns", []):
            if not self._severity_pass(severity):
                continue
            occurrences = self._find_in_lines(text, pattern)
            for line, col, matched in occurrences:
                detections.append(Detection(
                    text=matched,
                    category=category,
                    severity=severity,
                    line=line,
                    col=col,
                    length=len(matched),
                    description=f"过度修饰/模糊表达: '{matched}'",
                ))
        return detections

    def _detect_booster_words(
        self, text: str, rules: dict
    ) -> List[Detection]:
        """Detect booster/hype words.

        Uses word boundary matching to avoid partial matches.

        Args:
            text: The input text.
            rules: Detection rules dictionary.

        Returns:
            List of Detection objects for found booster words.
        """
        detections = []
        lines = text.split('\n')

        for line_idx, line in enumerate(lines):
            for word, category, severity in rules.get("booster_words", []):
                if not self._severity_pass(severity):
                    continue
                # Use regex with word boundaries for English
                if self.lang == "zh" or (
                    self.lang == "auto" and detect_language(text) == "zh"
                ):
                    # For Chinese, do substring matching
                    pos = 0
                    while True:
                        idx = line.find(word, pos)
                        if idx == -1:
                            break
                        detections.append(Detection(
                            text=word,
                            category=category,
                            severity=severity,
                            line=line_idx + 1,
                            col=idx + 1,
                            length=len(word),
                            description=f"夸大用语: '{word}'",
                        ))
                        pos = idx + 1
                else:
                    # For English, use word boundary regex
                    pattern = r'\b' + re.escape(word) + r'\b'
                    for match in re.finditer(pattern, line, re.IGNORECASE):
                        detections.append(Detection(
                            text=match.group(0),
                            category=category,
                            severity=severity,
                            line=line_idx + 1,
                            col=match.start() + 1,
                            length=len(match.group(0)),
                            description=f"夸大用语: '{match.group(0)}'",
                        ))

        return detections

    def analyze(self, text: str) -> DetectionResult:
        """Analyze text for AI-generated patterns.

        Performs a comprehensive scan of the input text using all
        detection rules for the configured language.

        Args:
            text: The input text to analyze.

        Returns:
            A DetectionResult containing all found detections and metadata.
        """
        lines = text.split('\n')

        # Determine language
        if self.lang == "auto":
            detected_lang = detect_language(text)
        else:
            detected_lang = self.lang

        # Get rules for the detected/specified language
        rules = self._get_rules(detected_lang)

        # Run all detectors
        all_detections: List[Detection] = []
        all_detections.extend(self._detect_cliche_phrases(text, rules))
        all_detections.extend(self._detect_structural_patterns(text, rules))
        all_detections.extend(self._detect_sentence_starters(text, rules))
        all_detections.extend(self._detect_hedge_patterns(text, rules))
        all_detections.extend(self._detect_booster_words(text, rules))

        # Sort detections by line number, then column
        all_detections.sort(key=lambda d: (d.line, d.col))

        return DetectionResult(
            detections=all_detections,
            total_lines=len(lines),
            total_chars=len(text),
            language=detected_lang,
        )
