# exile_ui_es/translations/guide.py
"""Guide instruction translator for Path of Exile leveling guides.

Handles instruction strings from [leveltracker] guide JSON files:
- Preserves markup tags: (color:red), (img:quest), (quest:amulet), etc.
- Preserves proper names: Hillock, Nessa, etc.
- Preserves area IDs, arena refs, angle-bracket refs, ;; locations
- Translates the instruction text to Spanish (LATAM).
"""

import re

# ── Proper names (NPCs, bosses — gold text in UI) ──────────────────────────
# These MUST NOT be translated.
PROPER_NAMES_LOWER: set[str] = {
    # User-provided list
    "hillock",
    "tarkleigh",
    "oak",
    "kraityn",
    "alira",
    "tolman",
    "arteri",
    "garukhan",
    "yeena",
    "irasha",
    "clarissa",
    "nessa",
    "bestel",
    "gruest",
    "piety",
    "dominus",
    "malachai",
    "kitava",
    "sin",
    "innocence",
    "silk",
    "utula",
    "vilenta",
    "lilly",
    "weylam",
    "lani",
    "hargan",
    "greust",
    "eramir",
    "bannon",
    # Additional names found in guide data
    "dweller",
    "fairgraves",
    "hailrake",
    "brutus",
    "merveil",
    "fidelitas",
    "weaver",
    "helena",
    "renly",
    "farrow",
    "una",
    "asinia",
    "beira",
    "the_bloated_miller",
    "blackjaw",
    "gravicius",
    "ekbab",
    "kabala",
    "krutog",
    "napuatzi",
    "rootdredge",
    "tor_gul",
    "shavronne",
    "maligaro",
    "doedre",
    "abberath",
    "daresso",
    "kaom",
    "tukohama",
    "gruthkul",
    "shakari",
    "arakali",
    "yugul",
    "brine_king",
    "solaris",
    "lunaris",
    "izario",
    "catarina",
    "jorgin",
    "aisling",
    "haku",
    "elreon",
    "vagan",
    "janus",
    "guff",
    "korell",
    "rin",
    "cameria",
    "it_that_fled",
    "leo",
    "tora",
    "zana",
    "alva",
    "jun",
    "niko",
    "einhar",
    "kirac",
    "cassia",
    "tane",
    "dannig",
    "rogh",
    "gwennen",
    "tujen",
    "faustus",
    "kalguur",
}


# ── Instruction translation dictionary ──────────────────────────────────────
# Keys are lowercase English phrases; values are Spanish equivalents.
# Multi-word phrases are matched with longest-match priority.
GUIDE_TRANSLATIONS: dict[str, str] = {
    # Directional compound phrases
    "follow wall": "seguir la pared",
    "follow edge": "seguir el borde",
    "follow road": "seguir el camino",
    "follow bridges/stairs": "seguir puentes/escaleras",
    "follow carpets": "seguir las alfombras",
    "follow the road": "seguir el camino",
    "follow streams": "seguir arroyos",
    "follow river": "seguir el río",
    "follow cliff": "seguir el acantilado",
    "top edge": "borde superior",
    "side path": "camino lateral",
    "main road": "camino principal",
    "long corners": "esquinas largas",
    "dead end": "callejón sin salida",
    "leads to": "lleva a",
    "connects to": "conecta con",
    "z-pattern": "patrón en z",
    "z-patterns": "patrones en z",
    "in the zone": "en la zona",
    "entering a room": "al entrar en una habitación",
    "large room": "habitación grande",
    "boss room": "sala del jefe",
    # Verbs
    "talk to": "hablar con",
    "pick up": "recoger",
    "enter": "entrar en",
    "return to": "volver a",
    "look for": "buscar",
    "go to": "ir a",
    "go": "ir",
    "find": "buscar",
    "find & enter": "buscar y entrar en",
    "find & kill": "buscar y matar",
    "activate": "activar",
    "check": "revisar",
    "search": "buscar",
    "take": "tomar",
    "get": "obtener",
    "equip": "equipar",
    "buy": "comprar",
    "sell": "vender",
    "craft": "fabricar",
    "set": "colocar",
    "open": "abrir",
    "move": "mover",
    "use": "usar",
    "complete": "completar",
    "break": "romper",
    "clear": "limpiar",
    "kill": "matar",
    "see": "ver",
    "look": "mirar",
    "drop": "soltar",
    "spare": "guardar",
    "skip": "saltar",
    "enable": "activar",
    "include": "incluir",
    "shows": "muestra",
    "showing": "mostrando",
    "imported": "importado",
    "synced": "sincronizado",
    "stay": "permanecer",
    "pointing": "apuntando",
    "points": "apunta",
    "start": "comenzar",
    "towards": "hacia",
    "unless": "a menos que",
    "wait": "esperar",
    # Nouns / objects
    "zone": "zona",
    "section": "sección",
    "edge": "borde",
    "wall": "pared",
    "corner": "esquina",
    "corners": "esquinas",
    "corridor": "pasillo",
    "bridge": "puente",
    "stairs": "escaleras",
    "road": "camino",
    "path": "camino",
    "ruins": "ruinas",
    "cage": "jaula",
    "beach": "playa",
    "shrine": "santuario",
    "cavern": "caverna",
    "cave": "cueva",
    "switch": "interruptor",
    "side": "lado",
    "exit": "salida",
    "center": "centro",
    "layout": "diseño",
    "stream": "arroyo",
    "streams": "arroyos",
    "boss": "jefe",
    "boat": "bote",
    "flow": "flujo",
    "water": "agua",
    "cliff": "acantilado",
    "prison": "prisión",
    "ledge": "saliente",
    "room": "habitación",
    "door": "puerta",
    "entrance": "entrada",
    "blocked": "bloqueado",
    "blockage": "bloqueo",
    "lever": "palanca",
    "gate": "portón",
    "passage": "pasaje",
    "trial": "prueba",
    "den": "guarida",
    "lair": "guarida",
    "camp": "campamento",
    "hut": "cabaña",
    "cave": "cueva",
    "arena": "arena",
    "checkpoint": "punto de control",
    "waypoint": "punto de ruta",
    "portal": "portal",
    "vendor": "vendedor",
    "vendors": "vendedores",
    "flask": "frasco",
    "flasks": "frascos",
    "quicksilver": "mercurio",
    "jewellery": "joyería",
    "ring": "anillo",
    "amulet": "amuleto",
    "belt": "cinturón",
    "boots": "botas",
    "gloves": "guantes",
    "helmet": "casco",
    "chest": "pechera",
    "weapon": "arma",
    "weapons": "armas",
    "wand": "varita",
    "sceptre": "cetro",
    "dagger": "daga",
    "claw": "garra",
    "sword": "espada",
    "axe": "hacha",
    "mace": "maza",
    "staff": "bastón",
    "bow": "arco",
    "shield": "escudo",
    "gem": "gema",
    "gems": "gemas",
    "skill": "habilidad",
    "support": "apoyo",
    "rune": "runa",
    "runes": "runas",
    "reward": "recompensa",
    "rewards": "recompensas",
    "item": "objeto",
    "items": "objetos",
    "quest": "misión",
    "optionals": "opcionales",
    "rogue": "renegado",
    "exiles": "exiliados",
    "bandit": "bandido",
    "bandits": "bandidos",
    "trial": "prueba",
    "trials": "pruebas",
    "lab": "lab",
    "labyrinth": "laberinto",
    "ascendancy": "ascendencia",
    "pantheon": "panteón",
    "god": "dios",
    "gods": "dioses",
    "soul": "alma",
    "spirit": "espíritu",
    "map": "mapa",
    "maps": "mapas",
    "essence": "esencia",
    "essences": "esencias",
    "strongbox": "caja fuerte",
    "chest": "cofre",
    "book": "libro",
    "tome": "tomo",
    "key": "llave",
    "keys": "llaves",
    "seal": "sello",
    "seals": "sellos",
    "statue": "estatua",
    "altar": "altar",
    "obelisk": "obelisco",
    "obelisks": "obeliscos",
    "glyph": "glifo",
    "glyphs": "glifos",
    "roots": "raíces",
    "mushrooms": "hongos",
    "tree": "árbol",
    "trees": "árboles",
    "flower-pot": "maceta",
    "carpets": "alfombras",
    "wagons": "carretas",
    "gallows": "horcas",
    "vines": "enredaderas",
    "statue": "estatua",
    "pillar": "pilar",
    "torch": "antorcha",
    "torches": "antorches",
    "fire": "fuego",
    "blood": "sangre",
    "corpse": "cadáver",
    "corpses": "cadáveres",
    "skeleton": "esqueleto",
    "skeletons": "esqueletos",
    "monster": "monstruo",
    "monsters": "monstruos",
    "pack": "grupo",
    "packs": "grupos",
    # Directions
    "above": "arriba",
    "below": "abajo",
    "left": "izquierda",
    "right": "derecha",
    "straight": "recto",
    "diagonally": "en diagonal",
    "direction": "dirección",
    "north": "norte",
    "south": "sur",
    "east": "este",
    "west": "oeste",
    # Prepositions / conjunctions / articles
    "for": "para",
    "to": "a",
    "in": "en",
    "on": "en",
    "at": "en",
    "with": "con",
    "or": "o",
    "and": "y",
    "then": "luego",
    "if": "si",
    "else": "si no",
    "of": "de",
    "from": "desde",
    "by": "por",
    "the": "el",
    # Adverbs / adjectives
    "first": "primero",
    "1st": "1.º",
    "main": "principal",
    "side": "lateral",
    "same": "mismo",
    "rest": "resto",
    "linear": "lineal",
    "usually": "generalmente",
    "instead": "en su lugar",
    "nearby": "cercano",
    "random": "aleatorio",
    "next": "siguiente",
    "optional": "opcional",
    "safer": "más seguro",
    "often": "a menudo",
    "rarely": "raramente",
    "sometimes": "a veces",
    "always": "siempre",
    "never": "nunca",
    "only": "solo",
    "also": "también",
    "very": "muy",
    "more": "más",
    "less": "menos",
    "far": "lejos",
    "near": "cerca",
    "around": "alrededor",
    "really": "realmente",
    "especially": "especialmente",
    # Time / sequence
    "before": "antes de",
    "after": "después de",
    "during": "durante",
    "until": "hasta",
    "while": "mientras",
    "once": "una vez",
    "again": "de nuevo",
    "still": "todavía",
    "already": "ya",
    # Compound phrases
    "whenever possible": "siempre que sea posible",
    "if possible": "si es posible",
    "as much as possible": "lo más posible",
    "as long as possible": "lo más lejos posible",
    "enemy at the gate": "enemigo en la puerta",
    "the coast": "la costa",
    "mud flats": "llanuras fangosas",
    "submerged passage": "pasaje sumergido",
    "the ledge": "el saliente",
    "the climb": "la escalada",
    "lower prison": "prisión inferior",
    "upper prison": "prisión superior",
    "prisoner's gate": "puerta del prisionero",
    "ship graveyard": "cementerio de barcos",
    "cavern of wrath": "caverna de la ira",
    "cavern of anger": "caverna de la furia",
    "southern forest": "bosque del sur",
    "forest encampment": "campamento del bosque",
    "old fields": "campos viejos",
    "the crossroads": "el cruce",
    "chamber of sins": "cámara de los pecados",
    "fellshrine ruins": "ruinas del santuario caído",
    "the crypt": "la cripta",
    "the riverways": "las vías fluviales",
    "western forest": "bosque occidental",
    "weaver's chambers": "cámaras de la tejedora",
    "broken bridge": "puente roto",
    "the wetlands": "los humedales",
    "vaal ruins": "ruinas vaal",
    "the northern forest": "el bosque del norte",
    "the caverns": "las cavernas",
    "the pyramid": "la pirámide",
    "the aqueduct": "el acueducto",
    "highgate": "puerta alta",
    "the dried lake": "el lago seco",
    "the mines": "las minas",
    "the crystal veins": "las venas de cristal",
    "daresso's dream": "el sueño de daresso",
    "the grand arena": "la gran arena",
    "the belly of the beast": "el vientre de la bestia",
    "the harvest": "la cosecha",
    "the shrine": "el santuario",
    "the templar courts": "los tribunales templarios",
    "the sceptre of god": "el cetro de dios",
    "the imperial gardens": "los jardines imperiales",
    "the lunaris temple": "el templo de lunaris",
    "the solaris temple": "el templo de solaris",
    "the ebony barracks": "los cuarteles de ébano",
    "the docks": "los muelles",
    "the battlefront": "el frente de batalla",
    "the marketplace": "el mercado",
    "the catacombs": "las catacumbas",
    "the library": "la biblioteca",
    "the archive": "el archivo",
    "the ossuary": "el osario",
    "the reliquary": "el relicario",
    "the tower": "la torre",
    "the coast": "la costa",
    "tidal island": "isla de la marea",
    "the den": "la guarida",
    "flooded depths": "profundidades inundadas",
    "ship graveyard cave": "cueva del cementerio de barcos",
    "broken bridge": "puente roto",
    # Guide-specific terms
    "leaguestart": "leaguestart",
    "twinkrun": "twinkrun",
    "relog": "relog",
    "scion": "scion",
    "hint": "pista",
    # Symbols (translated)
    "&": "y",
}

# ── Regex for preserved markup tokens ───────────────────────────────────────
# Tokens that MUST pass through untranslated.
# Groups are alternated; first match wins (leftmost).
_TOKEN_PATTERN = re.compile(
    r"\([^)]*\)"  # parenthesized markup: (color:red), (img:quest), (quest:amulet)
    r"|<[^>]*>"  # angle-bracket refs: <enemy_at_the_gate>, <2_respecs>
    r"|areaid[a-z0-9_]+\b"  # area IDs: areaid1_1_town, areaidg1_7
    r"|arena:[a-z_0-9]+\b"  # arena refs: arena:kraityn, arena:rotten_druid
    r"|;;.*$"  # ;; and everything after (location name / comment)
    r'|\b(?:leaguestart|twinkrun|optional|else|racestart|ssfstart|hcstart)\s*:'
    # mode/condition prefixes
    r"|\[MISSING\]"  # placeholder marker
)

# ── Pre-computed lookup structures ──────────────────────────────────────────

# Map each phrase to its translation
_PHRASE_MAP: dict[str, str] = {}
# Max phrase length in words
_MAX_PHRASE_LEN = 0

for _phrase, _translation in GUIDE_TRANSLATIONS.items():
    _phrase_lower = _phrase.lower().strip()
    _PHRASE_MAP[_phrase_lower] = _translation
    _word_count = len(_phrase_lower.split())
    if _word_count > _MAX_PHRASE_LEN:
        _MAX_PHRASE_LEN = _word_count


def _translate_text(text: str) -> str:
    """Translate a plain text segment — no markup tokens, just English words.

    Uses longest-match phrase lookup. Proper names pass through unchanged.
    Special case: "kill" → "matar a" when the next word is a proper name.
    """
    if not text.strip():
        return text

    # Split on whitespace while preserving it
    parts = re.split(r"(\s+)", text)
    # Collect word positions and whitespace
    words: list[str] = []
    whitespace: list[str] = []
    for p in parts:
        if p.isspace() or p == "":
            whitespace.append(p)
        else:
            words.append(p)

    if not words:
        return text

    translated_words: list[str] = []
    i = 0
    while i < len(words):
        word = words[i]

        # Non-alphabetic token (punctuation, symbols, numbers)
        if not re.search(r"[a-zA-Z]", word):
            lower = word.lower()
            if lower in _PHRASE_MAP:
                translated_words.append(_PHRASE_MAP[lower])
            else:
                translated_words.append(word)
            i += 1
            continue

        # Strip trailing punctuation for lookup
        clean_word = re.sub(r"[.,:;!?'\"]+$", "", word)
        trailing = word[len(clean_word) :]
        clean_lower = clean_word.lower()

        # Try longest phrase match
        matched = False
        max_len = min(_MAX_PHRASE_LEN, len(words) - i)

        for length in range(max_len, 0, -1):
            # Build phrase from clean, lowercased words
            phrase_parts: list[str] = []
            for j in range(i, i + length):
                w = words[j]
                cw = re.sub(r"[.,:;!?'\"]+$", "", w).lower()
                phrase_parts.append(cw)
            phrase = " ".join(phrase_parts)

            if phrase in _PHRASE_MAP:
                translation = _PHRASE_MAP[phrase]

                # Special case: "kill" followed by proper name → "matar a"
                if phrase == "kill" and i + 1 < len(words):
                    next_clean = re.sub(r"[.,:;!?'\"]+$", "", words[i + 1]).lower()
                    if next_clean in PROPER_NAMES_LOWER:
                        translation = "matar a"

                # Apply trailing punctuation from the LAST word of the phrase
                if length == 1:
                    translation = translation + trailing
                else:
                    # Multi-word phrase: trailing punctuation comes from last word
                    last_word = words[i + length - 1]
                    last_trailing = re.sub(r"^[a-zA-Z0-9'\-]+", "", last_word)
                    if last_trailing:
                        translation = translation + last_trailing

                translated_words.append(translation)
                i += length
                matched = True
                break

        if not matched:
            # Single word: check proper names, then single-word translations
            if clean_lower in PROPER_NAMES_LOWER:
                translated_words.append(clean_word + trailing)
            elif clean_lower in _PHRASE_MAP:
                translated_words.append(_PHRASE_MAP[clean_lower] + trailing)
            else:
                translated_words.append(word)  # Unknown, keep as-is
            i += 1

    # Reassemble with original whitespace
    if not whitespace:
        return " ".join(translated_words)

    # Interleave words and whitespace
    result_parts: list[str] = []
    wi = 0
    si = 0

    if parts and parts[0].isspace():
        result_parts.append(whitespace[si])
        si += 1

    while wi < len(translated_words):
        result_parts.append(translated_words[wi])
        wi += 1
        if si < len(whitespace):
            result_parts.append(whitespace[si])
            si += 1

    # Trailing whitespace
    while si < len(whitespace):
        result_parts.append(whitespace[si])
        si += 1

    return "".join(result_parts)


def translate_instruction(text: str) -> str:
    """Translate a single guide instruction string.

    Preserves all markup tokens, proper names, area IDs, arena refs,
    angle-bracket refs, and ;; location names.
    Translates only the plain English instruction text to Spanish.
    """
    if not text:
        return text

    # Find all preserved tokens
    matches = list(_TOKEN_PATTERN.finditer(text))

    if not matches:
        return _translate_text(text)

    result_parts: list[str] = []
    pos = 0

    for m in matches:
        # Translate text before this token
        if m.start() > pos:
            result_parts.append(_translate_text(text[pos : m.start()]))
        # Preserve the token itself
        result_parts.append(m.group(0))
        pos = m.end()

    # Translate remaining text after last token
    if pos < len(text):
        result_parts.append(_translate_text(text[pos:]))

    return "".join(result_parts)


def translate_guide(data: dict | list) -> dict | list:
    """Translate a leveling guide JSON structure.

    Recursively traverses the guide data, translating all instruction strings.
    The structure is:
      - Top level: list of acts
      - Each act: list of steps
      - Each step: either a list of strings, or a dict with "condition" and "lines"
    """
    if isinstance(data, list):
        return [translate_guide(item) for item in data]
    elif isinstance(data, dict):
        result: dict = {}
        for key, value in data.items():
            if key == "lines" and isinstance(value, list):
                # Translate instruction strings in "lines"
                result[key] = [
                    translate_instruction(line) if isinstance(line, str) else line
                    for line in value
                ]
            elif key == "condition":
                # Conditions are metadata, NOT translated
                result[key] = value
            else:
                result[key] = translate_guide(value)
        return result
    elif isinstance(data, str):
        # A string at the step level is an instruction to translate
        return translate_instruction(data)
    else:
        return data


def translate_guide_file(data: list, _source_file: str = "") -> list:
    """Translate a full guide JSON file.

    Wraps translate_guide but with an explicit list return type
    and accepts the source_file parameter for CLI compatibility.
    """
    result = translate_guide(data)
    if not isinstance(result, list):
        return [result]  # Shouldn't happen, but be safe
    return result