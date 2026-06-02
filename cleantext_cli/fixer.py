"""Auto-fix engine for AI text style issues.

Provides suggestions and automatic fixes for detected AI text patterns.
Supports both suggestion mode (show what to change) and auto-fix mode
(apply changes directly).
"""

from typing import Dict, List, Optional, Tuple

from cleantext_cli.detector import Detection, DetectionResult


class FixSuggestion:
    """A suggested fix for a detected AI text pattern.

    Attributes:
        detection: The original detection that triggered this suggestion.
        original: The original text fragment.
        replacement: The suggested replacement text.
        reason: Explanation of why this fix is recommended.
        confidence: Confidence level of the fix ('high', 'medium', 'low').
    """

    def __init__(
        self,
        detection: Detection,
        original: str,
        replacement: str,
        reason: str,
        confidence: str = "medium",
    ):
        self.detection = detection
        self.original = original
        self.replacement = replacement
        self.reason = reason
        self.confidence = confidence

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization.

        Returns:
            Dictionary representation of this suggestion.
        """
        return {
            "original": self.original,
            "replacement": self.replacement,
            "reason": self.reason,
            "confidence": self.confidence,
            "line": self.detection.line,
            "col": self.detection.col,
            "category": self.detection.category,
            "severity": self.detection.severity,
        }


class Fixer:
    """Auto-fix engine for AI text patterns.

    Generates fix suggestions for detected issues and can apply them
    automatically to produce cleaned text.
    """

    # Mapping of categories to default fix strategies
    FIX_STRATEGIES: Dict[str, str] = {
        "cliche_opening": "delete",
        "cliche_closing": "delete",
        "cliche_metaphor": "replace",
        "cliche_phrase": "replace",
        "overused_word": "replace",
        "booster_word": "replace",
        "filler_hedge": "delete",
        "transition_word": "simplify",
        "wordiness": "simplify",
        "binary_contrast": "restructure",
        "dramatic_opening": "restructure",
        "not_only_but_also": "simplify",
        "both_and": "simplify",
        "triple_list": "simplify",
        "whether_or": "simplify",
        "starter_in": "keep",       # Sentence starters are info-level, keep by default
        "starter_as": "keep",
        "starter_with": "keep",
        "starter_the": "keep",
        "hedge": "delete",
        "booster": "replace",
        "structural_cliche": "simplify",
        "enumeration_structure": "keep",
        "triple_climax": "simplify",
        "starter_hedge": "delete",
        "starter_summary": "keep",
        "starter_current": "keep",
        "starter_recent": "keep",
    }

    def __init__(self, confidence_threshold: str = "low"):
        """Initialize the fixer.

        Args:
            confidence_threshold: Minimum confidence level for auto-fix.
                One of 'high', 'medium', 'low'. Default 'low' applies all fixes.
        """
        self.confidence_levels = {"high": 3, "medium": 2, "low": 1}
        self.min_confidence = self.confidence_levels.get(confidence_threshold, 1)

    def _get_confidence_level(self, detection: Detection) -> int:
        """Determine confidence level for a fix suggestion.

        Args:
            detection: The detection to evaluate.

        Returns:
            Integer confidence level (3=high, 2=medium, 1=low).
        """
        strategy = self.FIX_STRATEGIES.get(detection.category, "keep")

        if detection.severity == "error" and detection.replacement:
            return 3  # High confidence
        elif detection.severity == "warning" and detection.replacement:
            return 2  # Medium confidence
        elif detection.replacement:
            return 2  # Medium confidence
        elif strategy == "delete":
            return 2  # Medium confidence for deletions
        else:
            return 1  # Low confidence

    def _generate_replacement(self, detection: Detection) -> str:
        """Generate a replacement string for a detection.

        Args:
            detection: The detection to generate a replacement for.

        Returns:
            The suggested replacement string (empty string for deletions).
        """
        strategy = self.FIX_STRATEGIES.get(detection.category, "keep")

        if strategy == "delete":
            return ""
        elif strategy == "keep":
            return detection.text  # No change
        elif detection.replacement:
            return detection.replacement
        else:
            return detection.text  # No change if no replacement available

    def suggest_fixes(
        self, result: DetectionResult
    ) -> List[FixSuggestion]:
        """Generate fix suggestions for all detections.

        Args:
            result: DetectionResult from the detector.

        Returns:
            List of FixSuggestion objects, sorted by position in text.
        """
        suggestions = []

        for detection in result.detections:
            strategy = self.FIX_STRATEGIES.get(detection.category, "keep")

            if strategy == "keep":
                continue  # Skip low-priority items

            confidence_level = self._get_confidence_level(detection)
            if confidence_level < self.min_confidence:
                continue

            replacement = self._generate_replacement(detection)

            # Determine reason
            if strategy == "delete":
                reason = f"删除AI风格表达 '{detection.text}'"
            elif strategy == "replace":
                reason = f"将 '{detection.text}' 替换为更自然的表达"
            elif strategy == "simplify":
                reason = f"简化冗余表达 '{detection.text}'"
            elif strategy == "restructure":
                reason = f"重构AI风格的句式结构"
            else:
                reason = f"优化 '{detection.text}'"

            confidence_str = {3: "high", 2: "medium", 1: "low"}.get(
                confidence_level, "low"
            )

            suggestions.append(FixSuggestion(
                detection=detection,
                original=detection.text,
                replacement=replacement,
                reason=reason,
                confidence=confidence_str,
            ))

        # Sort by line, then column
        suggestions.sort(key=lambda s: (s.detection.line, s.detection.col))

        return suggestions

    def apply_fixes(
        self, text: str, suggestions: List[FixSuggestion]
    ) -> str:
        """Apply fix suggestions to the text.

        Processes suggestions in reverse order (bottom to top) to avoid
        position shifts affecting subsequent replacements.

        Args:
            text: The original text.
            suggestions: List of FixSuggestion objects to apply.

        Returns:
            The fixed text with all suggestions applied.
        """
        if not suggestions:
            return text

        lines = text.split('\n')
        # Sort in reverse order to preserve positions
        sorted_suggestions = sorted(
            suggestions,
            key=lambda s: (s.detection.line, s.detection.col),
            reverse=True,
        )

        for suggestion in sorted_suggestions:
            line_num = suggestion.detection.line - 1  # Convert to 0-based
            col = suggestion.detection.col - 1  # Convert to 0-based

            if line_num < 0 or line_num >= len(lines):
                continue

            line = lines[line_num]
            original = suggestion.original
            replacement = suggestion.replacement

            # Find the original text at the expected position
            # Use case-insensitive matching
            line_lower = line.lower()
            original_lower = original.lower()

            search_pos = col
            pos = line_lower.find(original_lower, search_pos)

            if pos == -1:
                # Try finding anywhere on the line
                pos = line_lower.find(original_lower)
                if pos == -1:
                    continue

            # Perform the replacement
            before = line[:pos]
            after = line[pos + len(original):]

            # Handle whitespace around deletions
            if not replacement:
                # Clean up extra whitespace when deleting
                before = before.rstrip()
                if before and after and after[0] == ' ':
                    after = after[1:]
                elif before and not after:
                    pass  # End of line, just strip trailing space
                elif not before and after and after[0] == ' ':
                    after = after.lstrip(' ')

            lines[line_num] = before + replacement + after

        return '\n'.join(lines)

    def auto_fix(
        self, text: str, result: DetectionResult
    ) -> Tuple[str, List[FixSuggestion]]:
        """Automatically fix all detected issues in the text.

        Generates suggestions and applies them to produce cleaned text.

        Args:
            text: The original text.
            result: DetectionResult from the detector.

        Returns:
            Tuple of (fixed_text, applied_suggestions).
        """
        suggestions = self.suggest_fixes(result)
        fixed_text = self.apply_fixes(text, suggestions)
        return fixed_text, suggestions
