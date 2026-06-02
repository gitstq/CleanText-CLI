"""Pattern rules package for CleanText-CLI.

Exports rule loaders for English and Chinese AI text detection.
"""

from cleantext_cli.rules.en import get_all_rules as get_en_rules
from cleantext_cli.rules.zh import get_all_rules as get_zh_rules


def get_rules(lang: str) -> dict:
    """Get detection rules for the specified language.

    Args:
        lang: Language code, either 'en' or 'zh'.

    Returns:
        Dictionary of detection rules for the specified language.

    Raises:
        ValueError: If the language is not supported.
    """
    if lang == "en":
        return get_en_rules()
    elif lang == "zh":
        return get_zh_rules()
    else:
        raise ValueError(f"Unsupported language: {lang}. Use 'en' or 'zh'.")
