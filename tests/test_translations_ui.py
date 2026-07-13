from exile_ui_es.translations.ui import translate_ui, UI_TRANSLATIONS

SAMPLE = {
    "ms_general": "general",
    "ms_settings": "settings",
    "ms_actdecoder": "act-decoder",
    "ms_enchant": "enchant finder",
    "ms_betrayal": "betrayal-info",
    "ms_cheat_sheets": "cheat-sheets",
    "ms_clone": "clone-frames",
    "ms_donations": "donations",
    "ms_hotkeys": "hotkeys",
    "ms_item_info": "item-info",
    "ms_act_tracker": "act-tracker",
    "ms_chat": "chat macros",
    "ms_map_tracker": "map-tracker",
    "ms_map_info": "map-info",
    "ms_announce": "announcements",
    "ms_screen_checks": "screen-checks",
    "ms_search": "search-strings",
    "ms_stream": "stream-clients",
    "ms_qol": "minor qol tools",
}


def test_translate_ui_basic():
    result = translate_ui(SAMPLE)
    assert result["ms_general"] == "general"  # equal in Spanish
    assert "configuración" in result["ms_settings"].lower()
    assert result["ms_actdecoder"] == "decodificador de actos"
    assert result["ms_enchant"] == "buscador de encantamientos"
    assert result["ms_betrayal"] == "info de traición"
    assert result["ms_cheat_sheets"] == "hojas de referencia"
    assert result["ms_clone"] == "marcos clonados"
    assert result["ms_donations"] == "donaciones"
    assert result["ms_hotkeys"] == "atajos"
    assert result["ms_item_info"] == "info de objeto"
    assert result["ms_act_tracker"] == "rastreador de actos"
    assert result["ms_chat"] == "macros de chat"
    assert result["ms_map_tracker"] == "rastreador de mapas"
    assert result["ms_map_info"] == "info de mapa"
    assert result["ms_announce"] == "anuncios"
    assert result["ms_screen_checks"] == "verificaciones de pantalla"
    assert result["ms_search"] == "cadenas de búsqueda"
    assert result["ms_stream"] == "clientes de stream"
    assert result["ms_qol"] == "herramientas menores"
    assert len(result) == len(SAMPLE)


def test_translate_ui_unknown_string():
    """Unknown strings are passed through untranslated."""
    result = translate_ui({"custom_header": "some-new-feature"})
    assert result["custom_header"] == "some-new-feature"


def test_translate_ui_case_insensitive():
    """Translation lookup is case-insensitive."""
    result = translate_ui({"k1": "  General  "})
    assert result["k1"] == "general"


def test_translate_ui_empty():
    assert translate_ui({}) == {}


def test_translate_ui_all_terms_covered():
    """Every key in UI_TRANSLATIONS must have a unique lowercase key."""
    assert len(UI_TRANSLATIONS) == len(set(UI_TRANSLATIONS.values()))
    for term in UI_TRANSLATIONS.values():
        assert isinstance(term, str) and len(term) > 0