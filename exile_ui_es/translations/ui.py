# exile_ui_es/translations/ui.py

# UI strings — free translation, but keep consistency
UI_TRANSLATIONS: dict[str, str] = {
    "general": "general",
    "settings": "configuración",
    "act-decoder": "decodificador de actos",
    "enchant finder": "buscador de encantamientos",
    "betrayal-info": "info de traición",
    "cheat-sheets": "hojas de referencia",
    "clone-frames": "marcos clonados",
    "donations": "donaciones",
    "hotkeys": "atajos",
    "item-info": "info de objeto",
    "act-tracker": "rastreador de actos",
    "chat macros": "macros de chat",
    "map-tracker": "rastreador de mapas",
    "map-info": "info de mapa",
    "announcements": "anuncios",
    "screen-checks": "verificaciones de pantalla",
    "search-strings": "cadenas de búsqueda",
    "stream-clients": "clientes de stream",
    "minor qol tools": "herramientas menores",
}


def translate_ui(strings: dict[str, str]) -> dict[str, str]:
    """Translate UI strings to Spanish (LATAM)."""
    result = {}
    for key, value in strings.items():
        # Check if exact match in dictionary
        lower = value.lower().strip()
        if lower in UI_TRANSLATIONS:
            result[key] = UI_TRANSLATIONS[lower]
        else:
            # Keep untranslated for manual review
            result[key] = value
    return result