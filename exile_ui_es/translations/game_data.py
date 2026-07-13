# exile_ui_es/translations/game_data.py
import json
from pathlib import Path


# Load reference terms at module level
_TERMS_PATH = Path(__file__).parent.parent.parent / "data" / "poe_terms_es.json"
with open(_TERMS_PATH, encoding="utf-8") as f:
    _POE_TERMS = json.load(f)


def _build_translation_map() -> dict[str, str]:
    """Build a flat en→es translation map from all term categories."""
    mapping: dict[str, str] = {}
    for category in _POE_TERMS.values():
        if isinstance(category, dict):
            for en, es in category.items():
                mapping[en.lower()] = es
    return mapping


TERM_MAP = _build_translation_map()


def translate_game_data(data: dict | list, source_file: str) -> dict | list:
    """Translate game data JSON, preserving keys and translating leaf string values.

    Keys starting with '_' are metadata and never translated.
    Non-string leaf values (numbers, bools, null) are preserved as-is.
    """
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if key.startswith("_"):
                # Metadata keys — pass through untranslated
                result[key] = value
            else:
                result[key] = translate_game_data(value, source_file)
        return result
    elif isinstance(data, list):
        return [translate_game_data(item, source_file) for item in data]
    elif isinstance(data, str):
        lower = data.lower().strip()
        return TERM_MAP.get(lower, data)
    else:
        # Non-string leaf: int, float, bool, None — preserve
        return data