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

# Aplicar traducciones a una instalación de Exile-UI
uv run exile-ui-es apply --install /ruta/a/Exile-UI

# Crear un zip descargable con las traducciones aplicadas
uv run exile-ui-es bundle

# Restaurar los archivos originales en inglés
uv run exile-ui-es revert --install /ruta/a/Exile-UI
```

También podes usar el Makefile:

```bash
make pull       # Descargar
make translate  # Traducir
make patch      # Generar parches
make apply INSTALL=/ruta/a/Exile-UI   # Aplicar a instalación
make bundle     # Crear bundle zip
make revert INSTALL=/ruta/a/Exile-UI  # Restaurar inglés
make test       # Correr tests
```

## Comandos

| Comando | Descripción |
|---------|-------------|
| `pull` | Descarga los archivos de datos en inglés de la última versión de Exile-UI |
| `translate` | Traduce los archivos descargados al español (LATAM) |
| `patch` | Genera parches de diferencia entre inglés y español |
| `apply` | Aplica los parches y traducciones a una instalación de Exile-UI |
| `bundle` | Crea un zip completo de Exile-UI con las traducciones aplicadas |
| `revert` | Restaura los archivos originales en inglés desde el backup |

## Estructura

```
exile-ui-es/
├── exile_ui_es/            # Código fuente
│   ├── cli.py              # CLI principal (Click)
│   ├── downloader.py       # Descarga de GitHub Releases
│   ├── parser.py           # Parser de formato Exile-UI (.txt)
│   ├── patcher.py          # Generación/aplicación de parches (DeepDiff)
│   └── translations/       # Módulos de traducción
│       ├── ui.py            # Traducción de UI (libre)
│       ├── client.py        # Traducción de cliente (debe coincidir con el juego)
│       └── game_data.py     # Traducción de datos de juego (JSON)
├── data/
│   ├── poe_terms_es.json    # Referencia de términos oficiales de PoE en español
│   ├── patches/             # Parches de traducción generados
│   └── spanish/             # Traducciones completas generadas
├── downloads/               # Archivos originales descargados
├── tests/                   # Tests
├── Makefile
└── pyproject.toml
```

## Enfoque de traducción

| Archivo | Enfoque | Descripción |
|---------|---------|-------------|
| `UI.txt` | Traducción libre | Strings de la interfaz — se traducen libremente manteniendo consistencia con el juego |
| `client.txt` | Coincidencia exacta | Strings del cliente del juego — **deben coincidir exactamente** con lo que muestra PoE en español |
| `*.json` | Mixto | Nombres de items, mods, ligas usan traducción oficial; tooltips y descripciones se traducen |

## Términos de Path of Exile

El archivo `data/poe_terms_es.json` contiene la referencia de términos oficiales en español latinoamericano, organizados por categoría:

- **currency**: Orbes y moneda (Chaos Orb → Orbe del Caos, etc.)
- **leagues**: Ligas (Betrayal → Traición, Breach → Brecha, etc.)
- **item_classes**: Tipos de objeto (Body Armour → Armadura Corporal, etc.)
- **masters**: Maestros de Betrayal (nombres se preservan)
- **skill_gems**: Gemas de habilidad (Support → Asistencia, etc.)
- **mod_types**: Tipos de modificadores (Prefix → Prefijo, Suffix → Sufijo)

Para mantener las traducciones actualizadas, edita este archivo y volvé a correr `translate`.

## CI/CD

El workflow de GitHub Actions (`.github/workflows/build.yml`) corre automáticamente cada domingo y en cada push a `main`:

1. Corre los tests
2. Descarga la última versión de Exile-UI
3. Traduce al español
4. Genera parches
5. Crea un bundle zip
6. Sube el artefacto

## Licencia

MIT