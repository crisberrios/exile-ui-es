from exile_ui_es.parser import parse_txt, serialize_txt, translate_txt_file

SAMPLE = """
;## comment line
\tsystem_font\t=\t"Fontin SmallCaps"
\tms_general\t=\t"general"
\tgreeting\t=\t"line 1;line2"
"""


def test_parse_txt():
    result = parse_txt(SAMPLE)
    assert result["system_font"] == "Fontin SmallCaps"
    assert result["ms_general"] == "general"
    assert result["greeting"] == "line 1;line2"
    assert len(result) == 3


def test_serialize_txt_roundtrip():
    original = {"key1": "value1", "key2": "val with;semicolon"}
    txt = serialize_txt(original)
    parsed = parse_txt(txt)
    assert parsed == original


def test_translate_txt_file_preserves_comments():
    """Comments and structure must survive translation."""

    def noop_translate(data):
        return data  # No changes

    result = translate_txt_file(SAMPLE, noop_translate)
    assert ";## comment line" in result


def test_translate_txt_file_preserves_structure():
    """Empty lines and formatting must survive."""

    def noop_translate(data):
        return data

    result = translate_txt_file(SAMPLE, noop_translate)
    # Should have an empty line at start (from the SAMPLE's opening newline)
    assert result.startswith("\n")
    # Should have the tab-formatted key
    assert "\tsystem_font\t=\t" in result


def test_translate_txt_file_modifies_values():
    """Values are translated while structure is preserved."""

    def translate(data):
        return {k: v.upper() for k, v in data.items()}

    result = translate_txt_file(SAMPLE, translate)
    assert '"FONTIN SMALLCAPS"' in result
    assert '"GENERAL"' in result
    # Comments preserved
    assert ";## comment line" in result
    # Original tab formatting preserved
    assert "\tsystem_font\t=\t" in result


def test_translate_txt_file_unchanged_keys():
    """Keys not in the translation dict stay as-is."""

    def translate_partial(data):
        return {"ms_general": "configuración"}

    result = translate_txt_file(SAMPLE, translate_partial)
    assert '"configuración"' in result  # Changed
    assert '"Fontin SmallCaps"' in result  # Unchanged
    assert '"line 1;line2"' in result  # Unchanged