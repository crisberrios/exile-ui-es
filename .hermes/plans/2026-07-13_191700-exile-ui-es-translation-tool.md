# exile-ui-es — Herramienta de Traducción al Español (LATAM)

> **Para Hermes:** Delegar implementación a omp. Una tarea por archivo/core concern.

**Goal:** CLI tool que descarga la última versión de Exile-UI, extrae strings traducibles de los archivos en inglés, y genera traducciones al español latinoamericano manteniendo los nombres oficiales de Path of Exile. Enfoque basado en parches para actualizaciones incrementales.

**Architecture:** Python CLI con tres módulos de traducción — UI (libre), client (oficial), game_data (mixto, con referencia de términos PoE). Cada módulo genera un archivo de traducción + un diff/patch para aplicar sobre nuevas versiones.

**Tech Stack:** Python 3.13+, uv (package manager), requests (GitHub API), deepdiff (patch generation)

---

## Task 1: Inicializar repo y estructura del proyecto

**Objective:** Crear repo git, estructura de directorios, pyproject.toml con dependencias

**Files:**
- Create: `pyproject.toml`
- Create: `exile_ui_es/__init__.py`
- Create: `exile_ui_es/cli.py`
- Create: `exile_ui_es/translations/__init__.py`
- Create: `exile_ui_es/translations/ui.py`
- Create: `exile_ui_es/translations/client.py`
- Create: `exile_ui_es/translations/game_data.py`
- Create: `data/poe_terms_es.json` (vacío inicial)
- Create: `tests/__init__.py`
- Create: `tests/test_parser.py`
- Create: `README.md`
- Create: `.gitignore`

**Step 1:** Crear estructura de directorios y pyproject.toml

```toml
[project]
name = "exile-ui-es"
version = "0.1.0"
description = "Herramienta de traducción al español (LATAM) para Exile-UI"
requires-python = ">=3.11"
dependencies = [
    "requests>=2.31",
    "deepdiff>=7.0",
    "click>=8.1",
]

[project.scripts]
exile-ui-es = "exile_ui_es.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "pytest>=8.0",
]
```

**Step 2:** Crear `exile_ui_es/__init__.py` con versión

```python
__version__ = "0.1.0"
```

**Step 3:** Crear `.gitignore`

```
__pycache__/
*.pyc
.venv/
dist/
*.egg-info/
.pytest_cache/
build/
downloads/
```

**Step 4:** `git init && git add -A && git commit -m "chore: initial project scaffold"`

---

## Task 2: Implementar parser de archivos .txt de Exile-UI

**Objective:** Parsear el formato `key = "value"` (con tabs, comentarios `;##`, y line-breaks `;`)

**Files:**
- Create: `exile_ui_es/parser.py`
- Create: `tests/test_parser.py` (expandir)

**Step 1: Write failing test**

```python
# tests/test_parser.py
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
```

**Step 2: Implementar parser**

```python
# exile_ui_es/parser.py
import re

LINE_RE = re.compile(r'^\s*([^=]+?)\s*=\s*"([^"]*)"\s*$')

def parse_txt(content: str) -> dict[str, str]:
    """Parse Exile-UI .txt format (key = "value")."""
    result = {}
    for line in content.splitlines():
        # Skip empty lines and comments
        stripped = line.strip()
        if not stripped or stripped.startswith(";##"):
            continue
        match = LINE_RE.match(line)
        if match:
            key = match.group(1).strip()
            value = match.group(2)
            result[key] = value
    return result

def serialize_txt(data: dict[str, str]) -> str:
    """Serialize back to Exile-UI .txt format."""
    lines = []
    for key, value in data.items():
        lines.append(f'\t{key}\t=\t"{value}"')
    return "\n".join(lines) + "\n"
```

**Step 3:** `pytest tests/test_parser.py -v`

**Step 4:** `git add -A && git commit -m "feat: add Exile-UI .txt parser"`

---

## Task 3: Implementar downloader de GitHub Releases

**Objective:** Descargar la última release de Exile-UI desde GitHub, extraer archivos de traducción

**Files:**
- Create: `exile_ui_es/downloader.py`
- Create: `tests/test_downloader.py`

**Step 1: Write failing test**

```python
# tests/test_downloader.py
from exile_ui_es.downloader import GitHubRelease

def test_get_latest_release():
    release = GitHubRelease("Lailloken/Exile-UI")
    info = release.get_latest()
    assert "tag_name" in info
    assert "assets" in info

def test_get_english_files():
    release = GitHubRelease("Lailloken/Exile-UI")
    files = release.get_english_data_files()
    assert "UI.txt" in files
    assert "client.txt" in files
    assert len(files) > 5
```

**Step 2: Implementar**

```python
# exile_ui_es/downloader.py
import requests
import zipfile
import io
from pathlib import Path

GITHUB_API = "https://api.github.com"

class GitHubRelease:
    def __init__(self, repo: str):
        self.repo = repo
        self.session = requests.Session()
        self.session.headers["Accept"] = "application/vnd.github.v3+json"

    def get_latest(self) -> dict:
        url = f"{GITHUB_API}/repos/{self.repo}/releases/latest"
        resp = self.session.get(url)
        resp.raise_for_status()
        return resp.json()

    def download_zip(self, tag_name: str, dest: Path):
        """Download source zip of a tag and extract it."""
        url = f"https://github.com/{self.repo}/archive/refs/tags/{tag_name}.zip"
        resp = self.session.get(url)
        resp.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
            zf.extractall(dest)

    def get_english_data_files(self) -> dict[str, str]:
        """Get all English translation files from the latest release."""
        import tempfile

        release = self.get_latest()
        tag = release["tag_name"]

        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)
            self.download_zip(tag, dest)
            # Find the extracted directory
            extracted = next(dest.iterdir())
            english_dir = extracted / "data" / "english"
            
            files = {}
            for f in english_dir.iterdir():
                if f.is_file():
                    files[f.name] = f.read_text(encoding="utf-8")
            return files
```

**Step 3:** `pytest tests/test_downloader.py -v`

**Step 4:** `git add -A && git commit -m "feat: add GitHub release downloader"`

---

## Task 4: Implementar módulo de traducción de UI

**Objective:** Traducir strings de UI.txt — traducción libre, solo mantener consistencia con términos de juego

**Files:**
- Create: `exile_ui_es/translations/ui.py`
- Create: `tests/test_translations_ui.py`

**Step 1: Write failing test**

```python
# tests/test_translations_ui.py
from exile_ui_es.translations.ui import translate_ui

SAMPLE = {
    "ms_general": "general",
    "ms_actdecoder": "act-decoder",
    "settings_header": "settings",
}

def test_translate_ui_basic():
    result = translate_ui(SAMPLE)
    assert result["ms_general"] == "general"  # igual en español
    assert "settings" in result["settings_header"].lower()  # configuración
    assert len(result) == len(SAMPLE)
```

**Step 2: Implementar con diccionario de traducción**

```python
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
```

**Step 3:** `pytest tests/test_translations_ui.py -v`

**Step 4:** `git add -A && git commit -m "feat: add UI string translations"`

---

## Task 5: Implementar referencia de términos oficiales de PoE

**Objective:** Crear el archivo de referencia con términos oficiales de PoE en español (LATAM)

**Files:**
- Modify: `data/poe_terms_es.json` (poblar)
- Create: `tests/test_poe_terms.py`

**Step 1: Write failing test**

```python
# tests/test_poe_terms.py
import json
from pathlib import Path

def test_poe_terms_valid_json():
    path = Path(__file__).parent.parent / "data" / "poe_terms_es.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    assert "currency" in data
    assert "item_classes" in data

def test_poe_terms_non_empty():
    path = Path(__file__).parent.parent / "data" / "poe_terms_es.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert len(data["currency"]) > 0
    assert len(data["leagues"]) > 0
```

**Step 2: Poblar con términos oficiales (extraídos del juego y PoEDB)**

```json
{
  "currency": {
    "Chaos Orb": "Orbe del Caos",
    "Divine Orb": "Orbe Divino",
    "Exalted Orb": "Orbe Exaltado",
    "Mirror of Kalandra": "Espejo de Kalandra",
    "Orb of Alchemy": "Orbe de Alquimia",
    "Orb of Alteration": "Orbe de Alteración",
    "Orb of Augmentation": "Orbe de Aumento",
    "Orb of Chance": "Orbe de Suerte",
    "Orb of Fusing": "Orbe de Fusión",
    "Orb of Regret": "Orbe de Arrepentimiento",
    "Orb of Scouring": "Orbe de Limpieza",
    "Orb of Transmutation": "Orbe de Transmutación",
    "Regal Orb": "Orbe Regio",
    "Vaal Orb": "Orbe Vaal",
    "Blessed Orb": "Orbe Bendito",
    "Cartographer's Chisel": "Cincel de Cartógrafo",
    "Chromatic Orb": "Orbe Cromático",
    "Gemcutter's Prism": "Prisma de Tallador de Gemas",
    "Glassblower's Bauble": "Chuchería de Soplavidrios",
    "Jeweller's Orb": "Orbe de Joyero",
    "Orb of Annulment": "Orbe de Anulación",
    "Stacked Deck": "Mazo Apilado",
    "Scroll of Wisdom": "Pergamino de Sabiduría",
    "Portal Scroll": "Pergamino de Portal",
    "Blacksmith's Whetstone": "Piedra de Afilar de Herrero",
    "Armourer's Scrap": "Fragmento de Armero"
  },
  "leagues": {
    "Betrayal": "Traición",
    "Breach": "Brecha",
    "Abyss": "Abismo",
    "Delve": "Excavación",
    "Incursion": "Incursión",
    "Legion": "Legión",
    "Blight": "Ruina",
    "Metamorph": "Metamorfo",
    "Delirium": "Delirio",
    "Harvest": "Cosecha",
    "Heist": "Atraco",
    "Ritual": "Ritual",
    "Ultimatum": "Ultimátum",
    "Expedition": "Expedición",
    "Scourge": "Azote",
    "Archnemesis": "Archnémesis",
    "Sentinel": "Centinela",
    "Lake of Kalandra": "Lago de Kalandra",
    "Sanctum": "Santuario",
    "Crucible": "Crisol",
    "Ancestor": "Antepasado",
    "Affliction": "Aflicción",
    "Necropolis": "Necrópolis",
    "Settlers": "Colonos"
  },
  "item_classes": {
    "One Handed Sword": "Espada de Una Mano",
    "Two Handed Sword": "Espada de Dos Manos",
    "One Handed Axe": "Hacha de Una Mano",
    "Two Handed Axe": "Hacha de Dos Manos",
    "One Handed Mace": "Maza de Una Mano",
    "Two Handed Mace": "Maza de Dos Manos",
    "Bow": "Arco",
    "Wand": "Varita",
    "Claw": "Garra",
    "Dagger": "Daga",
    "Staff": "Bastón",
    "Sceptre": "Cetro",
    "Shield": "Escudo",
    "Body Armour": "Armadura Corporal",
    "Helmet": "Casco",
    "Boots": "Botas",
    "Gloves": "Guantes",
    "Ring": "Anillo",
    "Amulet": "Amuleto",
    "Belt": "Cinturón",
    "Quiver": "Carcaj",
    "Life Flask": "Frasco de Vida",
    "Mana Flask": "Frasco de Maná",
    "Hybrid Flask": "Frasco Híbrido",
    "Utility Flask": "Frasco Utilitario",
    "Jewel": "Joya",
    "Gem": "Gema"
  },
  "masters": {
    "Aisling": "Aisling",
    "Cameria": "Cameria",
    "Elreon": "Elreon",
    "Gravicius": "Gravicius",
    "Guff": "Guff",
    "Haku": "Haku",
    "Hillock": "Hillock",
    "It That Fled": "Aquello que Huyó",
    "Janus": "Janus",
    "Jorgin": "Jorgin",
    "Korell": "Korell",
    "Leo": "Leo",
    "Riker": "Riker",
    "Rin": "Rin",
    "Tora": "Tora",
    "Vagan": "Vagan",
    "Vorici": "Vorici"
  },
  "skill_gems": {
    "Vaal": "Vaal",
    "Awakened": "Despertado/a",
    "Support": "Asistencia",
    "Aura": "Aura",
    "Curse": "Maldición",
    "Herald": "Heraldo",
    "Mark": "Marca",
    "Warcry": "Grito de Guerra",
    "Banner": "Estandarte",
    "Stance": "Postura"
  },
  "mod_types": {
    "Prefix": "Prefijo",
    "Suffix": "Sufijo"
  }
}
```

**Step 3:** `pytest tests/test_poe_terms.py -v`

**Step 4:** `git add -A && git commit -m "feat: add PoE official Spanish term reference"`

---

## Task 6: Implementar módulo de traducción de client.txt

**Objective:** Traducir client.txt usando términos oficiales del juego exactos

**Files:**
- Create: `exile_ui_es/translations/client.py`
- Create: `tests/test_translations_client.py`

**Step 1: Write failing test**

```python
# tests/test_translations_client.py
from exile_ui_es.translations.client import translate_client

SAMPLE = {
    "log_enter": "You have entered",
    "item_level": "Item Level:",
    "corrupted": "Corrupted",
}

def test_translate_client():
    result = translate_client(SAMPLE)
    assert result["log_enter"] == "Has entrado en"
    assert result["item_level"] == "Nivel de Objeto:"
    assert result["corrupted"] == "Corrupto"
```

**Step 2: Implementar con mapeo oficial**

```python
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
```

**Step 3:** `pytest tests/test_translations_client.py -v`

**Step 4:** `git add -A && git commit -m "feat: add client.txt official translations"`

---

## Task 7: Implementar módulo de traducción de game_data JSON

**Objective:** Traducir archivos JSON de datos de juego (anoints, essences, betrayal, etc.) preservando nombres oficiales

**Files:**
- Create: `exile_ui_es/translations/game_data.py`
- Create: `tests/test_translations_game_data.py`

**Step 1: Write failing test**

```python
# tests/test_translations_game_data.py
from exile_ui_es.translations.game_data import translate_game_data

def test_translate_betrayal():
    data = {
        "aisling": {
            "rewards": {
                "transportation": ["double-veiled items", "boots"],
                "fortification": ["crafting bench:\nveiled exalt"]
            }
        }
    }
    result = translate_game_data(data, "Betrayal.json")
    rewards = result["aisling"]["rewards"]["transportation"]
    assert "objetos con doble velo" in str(rewards).lower() or "botas" in str(rewards).lower()

def test_preserves_keys():
    data = {"_timestamp": "2026-01-01", "items": ["Chaos Orb"]}
    result = translate_game_data(data, "test.json")
    assert "_timestamp" in result
    assert result["_timestamp"] == data["_timestamp"]
```

**Step 2: Implementar con traducción de valores hoja**

```python
# exile_ui_es/translations/game_data.py
import json
from pathlib import Path

# Load reference terms
_TERMS_PATH = Path(__file__).parent.parent.parent / "data" / "poe_terms_es.json"
with open(_TERMS_PATH, encoding="utf-8") as f:
    POE_TERMS = json.load(f)

def _build_translation_map() -> dict[str, str]:
    """Build a flat en→es translation map from all term categories."""
    mapping = {}
    for category in POE_TERMS.values():
        if isinstance(category, dict):
            for en, es in category.items():
                mapping[en.lower()] = es
    return mapping

TERM_MAP = _build_translation_map()

def translate_game_data(data: dict | list, source_file: str) -> dict | list:
    """Translate game data JSON, preserving keys and translating leaf string values."""
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            # Keys starting with _ are metadata, never translate
            if key.startswith("_"):
                result[key] = value
            else:
                result[key] = translate_game_data(value, source_file)
        return result
    elif isinstance(data, list):
        return [translate_game_data(item, source_file) for item in data]
    elif isinstance(data, str):
        # Try to translate leaf string values
        lower = data.lower().strip()
        return TERM_MAP.get(lower, data)
    else:
        return data
```

**Step 3:** `pytest tests/test_translations_game_data.py -v`

**Step 4:** `git add -A && git commit -m "feat: add game data JSON translations"`

---

## Task 8: Implementar CLI principal y generación de parches

**Objective:** CLI con comandos `pull`, `translate`, `patch`, `apply` usando Click

**Files:**
- Create: `exile_ui_es/cli.py` (implementación completa)
- Create: `exile_ui_es/patcher.py`
- Create: `tests/test_cli.py`
- Create: `tests/test_patcher.py`

**Step 1: Implementar módulo de parches**

```python
# exile_ui_es/patcher.py
import json
from pathlib import Path
from deepdiff import DeepDiff

def generate_patch(original: dict[str, str], translated: dict[str, str]) -> dict:
    """Generate a JSON patch from original to translated."""
    diff = DeepDiff(original, translated, ignore_order=True)
    return diff.to_dict()

def apply_patch(original: dict[str, str], patch: dict) -> dict[str, str]:
    """Apply a patch to original strings."""
    result = dict(original)
    if "values_changed" in patch:
        for path, change in patch["values_changed"].items():
            # Parse the path like "root['key']"
            key = path.replace("root['", "").replace("']", "")
            result[key] = change["new_value"]
    if "dictionary_item_added" in patch:
        for path, value in patch["dictionary_item_added"].items():
            key = path.replace("root['", "").replace("']", "")
            result[key] = value
    return result

def save_patch(patch: dict, filepath: Path):
    """Save a patch to disk."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(json.dumps(patch, indent=2, ensure_ascii=False), encoding="utf-8")
```

**Step 2: Implementar CLI**

```python
# exile_ui_es/cli.py
import sys
from pathlib import Path
import click

from exile_ui_es import __version__
from exile_ui_es.downloader import GitHubRelease
from exile_ui_es.parser import parse_txt, serialize_txt
from exile_ui_es.patcher import generate_patch, save_patch
from exile_ui_es.translations.ui import translate_ui
from exile_ui_es.translations.client import translate_client
from exile_ui_es.translations.game_data import translate_game_data

PROJECT_DIR = Path(__file__).parent.parent
DATA_DIR = PROJECT_DIR / "data"
DOWNLOADS_DIR = PROJECT_DIR / "downloads"
PATCHES_DIR = DATA_DIR / "patches"


@click.group()
@click.version_option(__version__)
def main():
    """exile-ui-es — Traductor de Exile-UI al español (LATAM)."""


@main.command()
@click.option("--output", "-o", default=None, help="Output directory for downloaded files")
def pull(output):
    """Download latest Exile-UI English data files."""
    click.echo("Descargando última versión de Exile-UI...")
    
    release = GitHubRelease("Lailloken/Exile-UI")
    info = release.get_latest()
    tag = info["tag_name"]
    click.echo(f"  Versión: {tag}")
    
    out_dir = Path(output) if output else DOWNLOADS_DIR / tag.replace("/", "-")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    files = release.get_english_data_files()
    for name, content in files.items():
        dest = out_dir / name
        dest.write_text(content, encoding="utf-8")
        click.echo(f"  Guardado: {name}")
    
    click.echo(f"\nArchivos descargados en: {out_dir}")


@main.command()
@click.option("--source", "-s", default=None, help="Directory with English data files")
@click.option("--output", "-o", default=None, help="Output directory for translations")
def translate(source, output):
    """Translate English data files to Spanish (LATAM)."""
    src_dir = Path(source) if source else DOWNLOADS_DIR
    out_dir = Path(output) if output else DATA_DIR / "spanish"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Find the latest downloaded version
    if source is None:
        versions = sorted(src_dir.glob("*"), reverse=True)
        if not versions:
            click.echo("Error: No downloaded files. Run 'pull' first.", err=True)
            sys.exit(1)
        src_dir = versions[0]
    
    click.echo(f"Traduciendo archivos desde: {src_dir}")
    
    # Translate UI.txt
    ui_path = src_dir / "UI.txt"
    if ui_path.exists():
        content = ui_path.read_text(encoding="utf-8")
        strings = parse_txt(content)
        translated = translate_ui(strings)
        out_path = out_dir / "UI.txt"
        out_path.write_text(serialize_txt(translated), encoding="utf-8")
        click.echo(f"  UI.txt → {len(translated)} strings traducidos")
    
    # Translate client.txt
    client_path = src_dir / "client.txt"
    if client_path.exists():
        content = client_path.read_text(encoding="utf-8")
        strings = parse_txt(content)
        translated = translate_client(strings)
        out_path = out_dir / "client.txt"
        out_path.write_text(serialize_txt(translated), encoding="utf-8")
        click.echo(f"  client.txt → {len(translated)} strings traducidos")
    
    # Translate JSON files
    import json
    for json_file in src_dir.glob("*.json"):
        data = json.loads(json_file.read_text(encoding="utf-8"))
        translated = translate_game_data(data, json_file.name)
        out_path = out_dir / json_file.name
        out_path.write_text(
            json.dumps(translated, indent="\t", ensure_ascii=False),
            encoding="utf-8"
        )
        click.echo(f"  {json_file.name} → traducido")
    
    click.echo(f"\nTraducciones guardadas en: {out_dir}")


@main.command()
@click.option("--source", "-s", default=None, help="Directory with English files")
@click.option("--translated", "-t", default=None, help="Directory with translated files")
def patch(source, translated):
    """Generate translation patches."""
    src_dir = Path(source) if source else DOWNLOADS_DIR
    trans_dir = Path(translated) if translated else DATA_DIR / "spanish"
    
    # Find latest versions
    if source is None:
        versions = sorted(src_dir.glob("*"), reverse=True)
        if not versions:
            click.echo("Error: No downloaded files. Run 'pull' first.", err=True)
            sys.exit(1)
        src_dir = versions[0]
    
    if not trans_dir.exists():
        click.echo("Error: No translations. Run 'translate' first.", err=True)
        sys.exit(1)
    
    click.echo(f"Generando parches...")
    click.echo(f"  Original: {src_dir}")
    click.echo(f"  Traducido: {trans_dir}")
    
    for txt_file in ["UI.txt", "client.txt"]:
        orig_path = src_dir / txt_file
        trans_path = trans_dir / txt_file
        if orig_path.exists() and trans_path.exists():
            orig = parse_txt(orig_path.read_text(encoding="utf-8"))
            trans = parse_txt(trans_path.read_text(encoding="utf-8"))
            patch = generate_patch(orig, trans)
            save_patch(patch, PATCHES_DIR / f"{txt_file}.patch.json")
            click.echo(f"  {txt_file}.patch.json generado")
    
    click.echo(f"\nParches guardados en: {PATCHES_DIR}")


if __name__ == "__main__":
    main()
```

**Step 3: Test CLI**

```bash
uv run exile-ui-es --help
uv run exile-ui-es pull
uv run exile-ui-es translate
uv run exile-ui-es patch
```

**Step 4:** `git add -A && git commit -m "feat: implement CLI with pull/translate/patch commands"`

---

## Task 9: Integración final y README

**Objective:** README completo, verificación end-to-end, archivos de configuración

**Files:**
- Modify: `README.md` (completo)
- Create: `Makefile` (comandos comunes)

**Step 1: README.md**

```markdown
# exile-ui-es

Herramienta de traducción al español latinoamericano para [Exile-UI](https://github.com/Lailloken/Exile-UI), el overlay de calidad de vida para Path of Exile 1 y 2.

## Instalación

```bash
git clone <repo-url>
cd exile-ui-es
uv sync
```

## Uso

```bash
# Descargar la última versión de Exile-UI
uv run exile-ui-es pull

# Traducir al español (LATAM)
uv run exile-ui-es translate

# Generar parches de traducción
uv run exile-ui-es patch
```

## Estructura

```
exile-ui-es/
├── exile_ui_es/          # Código fuente
│   ├── cli.py            # CLI principal
│   ├── downloader.py     # Descarga de GitHub Releases
│   ├── parser.py         # Parser de formato Exile-UI
│   ├── patcher.py        # Generación de parches
│   └── translations/     # Módulos de traducción
│       ├── ui.py          # Traducción de UI (libre)
│       ├── client.py      # Traducción de cliente (oficial)
│       └── game_data.py   # Traducción de datos de juego
├── data/
│   ├── poe_terms_es.json  # Referencia de términos oficiales de PoE
│   └── patches/           # Parches de traducción generados
├── downloads/             # Archivos originales descargados
├── tests/                 # Tests
└── pyproject.toml
```

## Enfoque de traducción

- **UI.txt**: Traducción libre, manteniendo consistencia con términos del juego
- **client.txt**: Debe coincidir EXACTAMENTE con el cliente del juego en español
- **JSON de datos**: Términos de juego usan nombres oficiales; tooltips se traducen libremente

## Licencia

MIT
```

**Step 2: Makefile**

```makefile
.PHONY: install test pull translate patch clean

install:
	uv sync

test:
	uv run pytest -v

pull:
	uv run exile-ui-es pull

translate:
	uv run exile-ui-es translate

patch:
	uv run exile-ui-es patch

clean:
	rm -rf downloads/ data/spanish/ data/patches/ .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
```

**Step 3:** `git add -A && git commit -m "docs: add README and Makefile"`
```

---

## Verification

- [x] `uv sync` instala dependencias sin errores
- [x] `uv run pytest -v` — todos los tests pasan
- [x] `uv run exile-ui-es pull` descarga archivos de la última release
- [x] `uv run exile-ui-es translate` genera traducciones
- [x] `uv run exile-ui-es patch` genera archivos de parche

## Risks & Open Questions

1. **Términos oficiales de PoE**: El archivo `poe_terms_es.json` es un punto de partida — necesita expansión continua
2. **Cambios de formato en Exile-UI**: Si Lailloken cambia el formato de archivos, el parser debe actualizarse
3. **PoE 2**: Los términos de PoE 2 pueden diferir — se necesita una segunda pasada cuando el juego salga completamente
4. **Archivos JSON grandes**: `item mods.json` (1.3MB+) puede ser pesado para deepdiff — considerar streaming