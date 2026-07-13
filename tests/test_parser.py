from exile_ui_es.parser import parse_txt, serialize_txt

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