# exile_ui_es/translations/client.py

# Official PoE Spanish (LATAM) client strings
# These MUST match what the game client displays EXACTLY
CLIENT_TRANSLATIONS: dict[str, str] = {
    # Enter/exit zones
    "You have entered": "Has entrado en",
    "You have entered #": "Has entrado en #",

    # Item info
    "Item Level:": "Nivel de Objeto:",
    "Quality:": "Calidad:",
    "Corrupted": "Corrupto",
    "Unidentified": "Sin identificar",
    "Mirrored": "Reflejado",
    "Sockets:": "Engarces:",
    "Requirements:": "Requisitos:",
    "Level:": "Nivel:",

    # Currency
    "Chaos Orb": "Orbe del Caos",
    "Divine Orb": "Orbe Divino",
    "Exalted Orb": "Orbe Exaltado",

    # Generic
    "Prefix": "Prefijo",
    "Suffix": "Sufijo",
    "Implicit": "Implícito",
    "Enchant": "Encantamiento",
}


def translate_client(strings: dict[str, str]) -> dict[str, str]:
    """Translate client.txt strings — must match official game translations."""
    result = {}
    for key, value in strings.items():
        result[key] = CLIENT_TRANSLATIONS.get(value, value)
    return result