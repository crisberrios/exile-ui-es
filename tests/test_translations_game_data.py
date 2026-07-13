# tests/test_translations_game_data.py
from exile_ui_es.translations.game_data import translate_game_data, TERM_MAP


def test_translate_betrayal_data():
    """Betrayal data with nested rewards is translated recursively."""
    data = {
        "aisling": {
            "_comment": "Aisling Laffrey rewards",
            "rewards": {
                "transportation": ["veiled items", "boots"],
                "fortification": ["crafting bench:\nveiled exalt"],
            },
        }
    }
    result = translate_game_data(data, "Betrayal.json")
    # Metadata key preserved
    assert "_comment" in result["aisling"]
    assert result["aisling"]["_comment"] == "Aisling Laffrey rewards"
    # String values are translated where terms match
    assert isinstance(result["aisling"]["rewards"]["transportation"], list)
    assert isinstance(result["aisling"]["rewards"]["fortification"], list)


def test_list_handling():
    """Lists are recursively traversed."""
    data = ["Chaos Orb", "Divine Orb", "Random String"]
    result = translate_game_data(data, "test.json")
    assert result[0] == "Orbe del Caos"
    assert result[1] == "Orbe Divino"
    assert result[2] == "Random String"  # Unknown → unchanged


def test_metadata_key_preservation():
    """Keys starting with '_' are never translated, and their values pass through."""
    data = {
        "_timestamp": "2026-01-01",
        "_version": 42,
        "_meta": {"nested_key": "Chaos Orb"},
        "items": ["Chaos Orb"],
    }
    result = translate_game_data(data, "test.json")
    assert "_timestamp" in result
    assert result["_timestamp"] == "2026-01-01"
    assert result["_version"] == 42
    # The value under _meta also passes through untranslated (recursive skip)
    assert result["_meta"]["nested_key"] == "Chaos Orb"
    # But non-metadata keys ARE translated
    assert result["items"][0] == "Orbe del Caos"


def test_non_string_leaf_preservation():
    """Non-string leaf values (int, float, bool, None) are preserved."""
    data = {"count": 5, "enabled": True, "ratio": 0.75, "empty": None}
    result = translate_game_data(data, "test.json")
    assert result["count"] == 5
    assert result["enabled"] is True
    assert result["ratio"] == 0.75
    assert result["empty"] is None


def test_nested_dicts():
    """Arbitrarily nested dicts are handled."""
    data = {"a": {"b": {"c": "Betrayal"}}}
    result = translate_game_data(data, "nested.json")
    assert result["a"]["b"]["c"] == "Traición"


def test_recursive_term_lookup():
    """Terms are matched case-insensitively and whitespace-stripped."""
    data = {"k1": "  betrayal  ", "k2": "BETRAYAL"}
    result = translate_game_data(data, "case.json")
    assert result["k1"] == "Traición"
    assert result["k2"] == "Traición"


def test_unknown_strings_unchanged():
    """Strings without a match in TERM_MAP are returned as-is."""
    data = {"key": "completely unknown string xyz"}
    result = translate_game_data(data, "unknown.json")
    assert result["key"] == "completely unknown string xyz"


def test_term_map_coverage():
    """TERM_MAP is non-empty and contains expected currencies."""
    assert len(TERM_MAP) > 0
    assert TERM_MAP.get("chaos orb") == "Orbe del Caos"
    assert TERM_MAP.get("divine orb") == "Orbe Divino"
    assert TERM_MAP.get("betrayal") == "Traición"