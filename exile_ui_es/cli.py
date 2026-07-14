# exile_ui_es/cli.py
import json
import shutil
import sys
from pathlib import Path

import click

from exile_ui_es import __version__
from exile_ui_es.downloader import GitHubRelease
from exile_ui_es.parser import parse_txt, serialize_txt
from exile_ui_es.patcher import generate_patch, apply_patch, save_patch
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
@click.option(
    "--output", "-o", default=None, help="Output directory for downloaded files"
)
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
@click.option(
    "--source", "-s", default=None, help="Directory with English data files"
)
@click.option(
    "--output", "-o", default=None, help="Output directory for translations"
)
def translate(source, output):
    """Translate English data files to Spanish (LATAM)."""
    src_dir = Path(source) if source else DOWNLOADS_DIR
    out_dir = Path(output) if output else DATA_DIR / "spanish"
    out_dir.mkdir(parents=True, exist_ok=True)

    if not src_dir.exists():
        click.echo(
            f"Error: Source directory not found: {src_dir}", err=True
        )
        sys.exit(1)

    # Find the latest downloaded version when using default source
    if source is None:
        versions = sorted(src_dir.glob("*"), reverse=True)
        if not versions:
            click.echo(
                "Error: No downloaded files. Run 'pull' first.", err=True
            )
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
    for json_file in src_dir.glob("*.json"):
        data = json.loads(json_file.read_text(encoding="utf-8"))
        translated = translate_game_data(data, json_file.name)
        out_path = out_dir / json_file.name
        out_path.write_text(
            json.dumps(translated, indent="\t", ensure_ascii=False),
            encoding="utf-8",
        )
        click.echo(f"  {json_file.name} → traducido")

    click.echo(f"\nTraducciones guardadas en: {out_dir}")


@main.command()
@click.option(
    "--source", "-s", default=None, help="Directory with English files"
)
@click.option(
    "--translated", "-t", default=None, help="Directory with translated files"
)
def patch(source, translated):
    """Generate translation patches."""
    src_dir = Path(source) if source else DOWNLOADS_DIR
    trans_dir = Path(translated) if translated else DATA_DIR / "spanish"

    if not src_dir.exists():
        click.echo(
            f"Error: Source directory not found: {src_dir}", err=True
        )
        sys.exit(1)

    # Find latest version when using default source
    if source is None:
        versions = sorted(src_dir.glob("*"), reverse=True)
        if not versions:
            click.echo(
                "Error: No downloaded files. Run 'pull' first.", err=True
            )
            sys.exit(1)
        src_dir = versions[0]

    if not trans_dir.exists():
        click.echo(
            "Error: No translations. Run 'translate' first.", err=True
        )
        sys.exit(1)

    click.echo("Generando parches...")
    click.echo(f"  Original: {src_dir}")
    click.echo(f"  Traducido: {trans_dir}")

    for txt_file in ["UI.txt", "client.txt"]:
        orig_path = src_dir / txt_file
        trans_path = trans_dir / txt_file
        if orig_path.exists() and trans_path.exists():
            orig = parse_txt(orig_path.read_text(encoding="utf-8"))
            trans = parse_txt(trans_path.read_text(encoding="utf-8"))
            patch_data = generate_patch(orig, trans)
            save_patch(patch_data, PATCHES_DIR / f"{txt_file}.patch.json")
            click.echo(f"  {txt_file}.patch.json generado")

    click.echo(f"\nParches guardados en: {PATCHES_DIR}")


@main.command()
@click.option(
    "--install", "-i", required=True, help="Path to Exile-UI installation root"
)
def apply(install):
    """Patch an Exile-UI installation with Spanish translations."""
    install_dir = Path(install)
    english_dir = install_dir / "data" / "english"
    backup_dir = install_dir / "data" / "english.backup"

    if not english_dir.exists():
        click.echo(
            f"Error: data/english not found in {install_dir}", err=True
        )
        sys.exit(1)

    # Backup originals once
    if not backup_dir.exists():
        shutil.copytree(english_dir, backup_dir)
        click.echo(f"Backup creado en: {backup_dir}")

    # Apply .txt patches
    for patch_file in PATCHES_DIR.glob("*.patch.json"):
        base_name = patch_file.name.replace(".patch.json", "")
        orig_path = english_dir / base_name
        if orig_path.exists():
            orig = parse_txt(orig_path.read_text(encoding="utf-8"))
            patch_data = json.loads(patch_file.read_text(encoding="utf-8"))
            patched = apply_patch(orig, patch_data)
            orig_path.write_text(serialize_txt(patched), encoding="utf-8")
            click.echo(f"  {base_name} → parcheado")

    # Copy Spanish JSON files
    spanish_dir = DATA_DIR / "spanish"
    if spanish_dir.exists():
        for json_file in spanish_dir.glob("*.json"):
            dest = english_dir / json_file.name
            shutil.copy2(json_file, dest)
            click.echo(f"  {json_file.name} → copiado")

    click.echo(f"\nInstalación parcheada en: {install_dir}")


@main.command()
@click.option(
    "--output", "-o", default=None, help="Output directory for the bundle"
)
def bundle(output):
    """Create a downloadable zip artifact with Spanish translations."""
    import tempfile

    release = GitHubRelease("Lailloken/Exile-UI")

    out_dir = Path(output) if output else DOWNLOADS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        tag = release.download_full_release(tmp_path)
        extracted = next(tmp_path.iterdir())
        english_dir = extracted / "data" / "english"

        # Apply .txt patches
        for patch_file in PATCHES_DIR.glob("*.patch.json"):
            base_name = patch_file.name.replace(".patch.json", "")
            orig_path = english_dir / base_name
            if orig_path.exists():
                orig = parse_txt(orig_path.read_text(encoding="utf-8"))
                patch_data = json.loads(
                    patch_file.read_text(encoding="utf-8")
                )
                patched = apply_patch(orig, patch_data)
                orig_path.write_text(serialize_txt(patched), encoding="utf-8")
                click.echo(f"  {base_name} → parcheado")

        # Copy Spanish JSON files
        spanish_dir = DATA_DIR / "spanish"
        if spanish_dir.exists():
            for json_file in spanish_dir.glob("*.json"):
                dest = english_dir / json_file.name
                shutil.copy2(json_file, dest)
                click.echo(f"  {json_file.name} → copiado")

        # Create zip
        bundle_name = f"Exile-UI-es-{tag}.zip"
        bundle_path = out_dir / bundle_name
        shutil.make_archive(
            str(bundle_path.with_suffix("")),
            "zip",
            extracted.parent,
            extracted.name,
        )
        click.echo(f"\nBundle creado: {bundle_path}")


@main.command()
@click.option(
    "--install", "-i", required=True, help="Path to Exile-UI installation root"
)
def revert(install):
    """Restore English from backup."""
    install_dir = Path(install)
    backup_dir = install_dir / "data" / "english.backup"
    english_dir = install_dir / "data" / "english"

    if not backup_dir.exists():
        click.echo(
            f"Error: Backup not found at {backup_dir}", err=True
        )
        sys.exit(1)

    # Remove current English and restore from backup
    if english_dir.exists():
        shutil.rmtree(english_dir)
    shutil.copytree(backup_dir, english_dir)
    click.echo(f"Restaurado desde: {backup_dir}")


if __name__ == "__main__":
    main()