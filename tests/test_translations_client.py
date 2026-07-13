from exile_ui_es.translations.client import translate_client, CLIENT_TRANSLATIONS

SAMPLE = {
    "log_enter": "You have entered",
    "item_level": "Item Level:",
    "corrupted": "Corrupted",
    "unidentified": "Unidentified",
    "mirrored": "Mirrored",
}


def test_translate_client_basic():
    result = translate_client(SAMPLE)
    assert result["log_enter"] == "Has entrado en"
    assert result["item_level"] == "Nivel de Objeto:"
    assert result["corrupted"] == "Corrupto"
    assert result["unidentified"] == "Sin identificar"
    assert result["mirrored"] == "Reflejado"


def test_translate_client_all_terms():
    """Verify every term in the dictionary maps to a non-empty translation."""
    strings = {f"k{i}": term for i, term in enumerate(CLIENT_TRANSLATIONS)}
    result = translate_client(strings)
    for key in strings:
        assert result[key] == CLIENT_TRANSLATIONS[strings[key]]
        assert len(result[key]) > 0


def test_translate_client_unknown():
    """Unknown strings pass through untranslated."""
    result = translate_client({"some_key": "totally unknown string"})
    assert result["some_key"] == "totally unknown string"


def test_translate_client_empty():
    assert translate_client({}) == {}


def test_translate_client_quality():
    result = translate_client({"q": "Quality:"})
    assert result["q"] == "Calidad:"


def test_translate_client_sockets():
    result = translate_client({"s": "Sockets:"})
    assert result["s"] == "Engarces:"


def test_translate_client_requirements():
    result = translate_client({"r": "Requirements:"})
    assert result["r"] == "Requisitos:"


def test_translate_client_level():
    result = translate_client({"l": "Level:"})
    assert result["l"] == "Nivel:"


def test_translate_client_implicit():
    result = translate_client({"i": "Implicit"})
    assert result["i"] == "Implícito"


def test_translate_client_enchant():
    result = translate_client({"e": "Enchant"})
    assert result["e"] == "Encantamiento"


def test_translate_client_enter_with_hash():
    result = translate_client({"enter": "You have entered #"})
    assert result["enter"] == "Has entrado en #"