"""Scoring engine for AI text analysis.

Evaluates text on a 1-10 scale across multiple dimensions:
directness, rhythm, trustworthiness, authenticity, and density.
Provides an overall score with a detailed breakdown.
"""

from dataclasses import dataclass, field
from typing import Dict, List

from cleantext_cli.detector import Detection, DetectionResult


@dataclass
class DimensionScore:
    """Score for a single evaluation dimension.

    Attributes:
        name: Name of the dimension (e.g. 'directness', 'rhythm').
        score: Score from 1 to 10 (10 = best, most human-like).
        weight: Weight of this dimension in the overall score (0.0 to 1.0).
        details: Human-readable explanation of the score.
    """
    name: str
    score: float
    weight: float
    details: str = ""


@dataclass
class ScoreReport:
    """Complete scoring report for a text analysis.

    Attributes:
        overall: Overall score from 1 to 10 (10 = most human-like).
        dimensions: Individual dimension scores.
        detection_count: Total number of detections found.
        severity_counts: Counts by severity level.
        grade: Letter grade (A+ through F).
    """
    overall: float
    dimensions: List[DimensionScore] = field(default_factory=list)
    detection_count: int = 0
    severity_counts: Dict[str, int] = field(default_factory=dict)
    grade: str = ""


class Scorer:
    """Text quality scorer.

    Evaluates text based on detection results and text statistics
    to produce a multi-dimensional quality score.

    The scoring dimensions are:
    - Directness (weight 0.25): How directly the text communicates.
    - Rhythm (weight 0.20): Variety in sentence length and structure.
    - Trustworthiness (weight 0.25): Absence of hedging and booster words.
    - Authenticity (weight 0.20): Absence of cliché phrases and patterns.
    - Density (weight 0.10): Information density vs filler content.
    """

    # Category weights for penalty calculation
    CATEGORY_PENALTIES: Dict[str, float] = {
        "cliche_opening": 1.5,
        "cliche_closing": 1.2,
        "cliche_metaphor": 1.0,
        "cliche_phrase": 0.8,
        "overused_word": 0.6,
        "booster_word": 0.7,
        "filler_hedge": 0.5,
        "transition_word": 0.3,
        "wordiness": 0.4,
        "binary_contrast": 0.6,
        "dramatic_opening": 0.8,
        "not_only_but_also": 0.3,
        "both_and": 0.3,
        "triple_list": 0.4,
        "whether_or": 0.5,
        "starter_in": 0.2,
        "starter_as": 0.2,
        "starter_with": 0.2,
        "starter_the": 0.2,
        "hedge": 0.4,
        "booster": 0.6,
        "structural_cliche": 0.5,
        "enumeration_structure": 0.3,
        "triple_climax": 0.5,
        "starter_hedge": 0.4,
        "starter_summary": 0.3,
        "starter_current": 0.2,
        "starter_recent": 0.2,
    }

    SEVERITY_MULTIPLIERS: Dict[str, float] = {
        "info": 0.5,
        "warning": 1.0,
        "error": 1.5,
    }

    def __init__(self):
        """Initialize the scorer with default settings."""
        pass

    def _count_severities(self, detections: List[Detection]) -> Dict[str, int]:
        """Count detections by severity level.

        Args:
            detections: List of Detection objects.

        Returns:
            Dictionary mapping severity to count.
        """
        counts: Dict[str, int] = {"info": 0, "warning": 0, "error": 0}
        for d in detections:
            if d.severity in counts:
                counts[d.severity] += 1
        return counts

    def _calculate_penalty(self, detections: List[Detection]) -> float:
        """Calculate a cumulative penalty score from detections.

        Higher penalty means more AI-like text.

        Args:
            detections: List of Detection objects.

        Returns:
            Cumulative penalty score (0.0 or higher).
        """
        penalty = 0.0
        for d in detections:
            cat_penalty = self.CATEGORY_PENALTIES.get(d.category, 0.5)
            sev_mult = self.SEVERITY_MULTIPLIERS.get(d.severity, 1.0)
            penalty += cat_penalty * sev_mult
        return penalty

    def _score_directness(
        self, detections: List[Detection], text: str
    ) -> DimensionScore:
        """Score text directness.

        Measures how directly the text communicates without filler,
        hedging, or unnecessary padding.

        Args:
            detections: List of Detection objects.
            text: The original text.

        Returns:
            DimensionScore for directness.
        """
        # Count filler/hedge/wordiness detections
        filler_count = sum(
            1 for d in detections
            if d.category in ("filler_hedge", "wordiness", "hedge")
        )
        # Count cliche openings/closings
        bookend_count = sum(
            1 for d in detections
            if d.category in ("cliche_opening", "cliche_closing")
        )

        # Base score starts at 10, subtract penalties
        score = 10.0
        score -= filler_count * 0.8
        score -= bookend_count * 1.2

        # Adjust for text length (longer text tolerates more filler)
        lines = text.split('\n')
        if len(lines) > 10:
            score = min(10.0, score + (len(lines) - 10) * 0.05)

        score = max(1.0, min(10.0, score))

        details_parts = []
        if filler_count > 0:
            details_parts.append(f"发现 {filler_count} 处填充词/模糊表达")
        if bookend_count > 0:
            details_parts.append(f"发现 {bookend_count} 处套话开头/结尾")
        if not details_parts:
            details_parts.append("文本表达直接，无明显填充")

        return DimensionScore(
            name="directness",
            score=round(score, 1),
            weight=0.25,
            details="; ".join(details_parts),
        )

    def _score_rhythm(self, detections: List[Detection], text: str) -> DimensionScore:
        """Score text rhythm and structural variety.

        Measures variety in sentence length, paragraph structure,
        and absence of repetitive patterns.

        Args:
            detections: List of Detection objects.
            text: The original text.

        Returns:
            DimensionScore for rhythm.
        """
        import re

        # Split into sentences
        sentences = re.split(r'[.!?。！？\n]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return DimensionScore(
                name="rhythm",
                score=5.0,
                weight=0.20,
                details="无法分析句子节奏",
            )

        # Calculate sentence lengths (in characters)
        lengths = [len(s) for s in sentences]

        # Calculate variance in sentence length
        if len(lengths) > 1:
            mean_len = sum(lengths) / len(lengths)
            variance = sum((l - mean_len) ** 2 for l in lengths) / len(lengths)
            std_dev = variance ** 0.5

            # Higher variance = better rhythm (up to a point)
            if mean_len > 0:
                cv = std_dev / mean_len  # Coefficient of variation
                rhythm_score = min(10.0, 5.0 + cv * 5)
            else:
                rhythm_score = 5.0
        else:
            rhythm_score = 5.0

        # Penalize for structural clichés
        structural_count = sum(
            1 for d in detections
            if d.category in (
                "binary_contrast", "dramatic_opening", "not_only_but_also",
                "both_and", "triple_list", "whether_or", "enumeration_structure",
                "triple_climax", "structural_cliche",
            )
        )
        rhythm_score -= structural_count * 0.5

        # Penalize for repetitive sentence starters
        starter_count = sum(
            1 for d in detections
            if d.category.startswith("starter_")
        )
        if len(sentences) > 0 and starter_count / max(len(sentences), 1) > 0.3:
            rhythm_score -= 1.0

        rhythm_score = max(1.0, min(10.0, rhythm_score))

        details_parts = []
        if structural_count > 0:
            details_parts.append(f"发现 {structural_count} 处结构陈词滥调")
        if starter_count > 2:
            details_parts.append(f"发现 {starter_count} 处重复句首模式")
        if cv if len(lengths) > 1 else 0 < 0.3:
            details_parts.append("句子长度变化不足，节奏单调")
        if not details_parts:
            details_parts.append("句子节奏自然，结构有变化")

        return DimensionScore(
            name="rhythm",
            score=round(rhythm_score, 1),
            weight=0.20,
            details="; ".join(details_parts),
        )

    def _score_trustworthiness(
        self, detections: List[Detection], text: str
    ) -> DimensionScore:
        """Score text trustworthiness.

        Measures absence of excessive hedging and booster words
        that undermine credibility.

        Args:
            detections: List of Detection objects.
            text: The original text.

        Returns:
            DimensionScore for trustworthiness.
        """
        # Count hedge and booster detections
        hedge_count = sum(
            1 for d in detections
            if d.category in ("hedge", "filler_hedge", "starter_hedge")
        )
        booster_count = sum(
            1 for d in detections
            if d.category in ("booster_word", "booster")
        )

        score = 10.0
        score -= hedge_count * 0.6
        score -= booster_count * 0.8

        # Bonus for balanced tone (not too many of either)
        total = hedge_count + booster_count
        if total > 0:
            balance = abs(hedge_count - booster_count) / total
            if balance < 0.3:  # Well-balanced
                score += 0.5

        score = max(1.0, min(10.0, score))

        details_parts = []
        if hedge_count > 0:
            details_parts.append(f"发现 {hedge_count} 处模糊表达")
        if booster_count > 0:
            details_parts.append(f"发现 {booster_count} 处夸大用语")
        if not details_parts:
            details_parts.append("语气平衡可信，无过度修饰")

        return DimensionScore(
            name="trustworthiness",
            score=round(score, 1),
            weight=0.25,
            details="; ".join(details_parts),
        )

    def _score_authenticity(
        self, detections: List[Detection], text: str
    ) -> DimensionScore:
        """Score text authenticity.

        Measures absence of cliché phrases, metaphors, and
        overused words that signal AI-generated text.

        Args:
            detections: List of Detection objects.
            text: The original text.

        Returns:
            DimensionScore for authenticity.
        """
        # Count all cliche and overused word detections
        cliche_count = sum(
            1 for d in detections
            if d.category in (
                "cliche_opening", "cliche_closing", "cliche_metaphor",
                "cliche_phrase", "overused_word",
            )
        )

        # Calculate penalty ratio relative to text length
        lines = text.split('\n')
        non_empty_lines = [l for l in lines if l.strip()]
        ratio = cliche_count / max(len(non_empty_lines), 1)

        score = 10.0
        score -= cliche_count * 0.7

        # Extra penalty if density is very high
        if ratio > 0.5:
            score -= 2.0
        elif ratio > 0.3:
            score -= 1.0

        score = max(1.0, min(10.0, score))

        details_parts = []
        if cliche_count > 0:
            details_parts.append(f"发现 {cliche_count} 处AI风格短语/陈词滥调")
        if ratio > 0.3:
            details_parts.append(f"陈词滥调密度过高 ({ratio:.0%})")
        if not details_parts:
            details_parts.append("文本表达自然，无明显AI痕迹")

        return DimensionScore(
            name="authenticity",
            score=round(score, 1),
            weight=0.20,
            details="; ".join(details_parts),
        )

    def _score_density(
        self, detections: List[Detection], text: str
    ) -> DimensionScore:
        """Score information density.

        Measures the ratio of meaningful content to filler words
        and padding phrases.

        Args:
            detections: List of Detection objects.
            text: The original text.

        Returns:
            DimensionScore for density.
        """
        import re

        # Count wordiness and transition word detections
        wordiness_count = sum(
            1 for d in detections
            if d.category in ("wordiness", "transition_word")
        )

        # Calculate average sentence length (shorter = more dense usually)
        sentences = re.split(r'[.!?。！？\n]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return DimensionScore(
                name="density",
                score=5.0,
                weight=0.10,
                details="无法分析信息密度",
            )

        avg_length = sum(len(s) for s in sentences) / len(sentences)

        score = 10.0
        score -= wordiness_count * 0.5

        # Very long sentences may indicate padding
        long_sentences = sum(1 for s in sentences if len(s) > 200)
        if long_sentences > 0:
            score -= long_sentences * 0.3

        # Very short sentences may indicate lack of substance
        short_sentences = sum(1 for s in sentences if len(s) < 10)
        if len(sentences) > 3 and short_sentences / len(sentences) > 0.5:
            score -= 0.5

        score = max(1.0, min(10.0, score))

        details_parts = []
        if wordiness_count > 0:
            details_parts.append(f"发现 {wordiness_count} 处冗余表达")
        if long_sentences > 0:
            details_parts.append(f"有 {long_sentences} 个过长句子")
        if not details_parts:
            details_parts.append("信息密度良好")

        return DimensionScore(
            name="density",
            score=round(score, 1),
            weight=0.10,
            details="; ".join(details_parts),
        )

    def _calculate_grade(self, overall: float) -> str:
        """Convert numeric score to letter grade.

        Args:
            overall: Overall score from 1 to 10.

        Returns:
            Letter grade from 'A+' to 'F'.
        """
        if overall >= 9.0:
            return "A+"
        elif overall >= 8.5:
            return "A"
        elif overall >= 8.0:
            return "A-"
        elif overall >= 7.5:
            return "B+"
        elif overall >= 7.0:
            return "B"
        elif overall >= 6.5:
            return "B-"
        elif overall >= 6.0:
            return "C+"
        elif overall >= 5.5:
            return "C"
        elif overall >= 5.0:
            return "C-"
        elif overall >= 4.0:
            return "D"
        else:
            return "F"

    def score(
        self, result: DetectionResult, text: str
    ) -> ScoreReport:
        """Generate a comprehensive score report.

        Args:
            result: DetectionResult from the detector.
            text: The original analyzed text.

        Returns:
            A ScoreReport with overall score, dimension breakdown, and grade.
        """
        detections = result.detections

        # Calculate individual dimension scores
        dimensions = [
            self._score_directness(detections, text),
            self._score_rhythm(detections, text),
            self._score_trustworthiness(detections, text),
            self._score_authenticity(detections, text),
            self._score_density(detections, text),
        ]

        # Calculate weighted overall score
        overall = sum(d.score * d.weight for d in dimensions)
        overall = round(max(1.0, min(10.0, overall)), 1)

        # Count severities
        severity_counts = self._count_severities(detections)

        # Calculate grade
        grade = self._calculate_grade(overall)

        return ScoreReport(
            overall=overall,
            dimensions=dimensions,
            detection_count=len(detections),
            severity_counts=severity_counts,
            grade=grade,
        )
