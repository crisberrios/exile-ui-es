# tests/test_cli.py
import json
import tempfile
from pathlib import Path

from click.testing import CliRunner

from exile_ui_es.cli import main
from exile_ui_es.parser import parse_txt, serialize_txt
from exile_ui_es.patcher import generate_patch, save_patch


def test_cli_help():
    """CLI shows help without errors."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "exile-ui-es" in result.output


def test_cli_version():
    """CLI shows version."""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_cli_pull_help():
    """pull subcommand shows help."""
    runner = CliRunner()
    result = runner.invoke(main, ["pull", "--help"])
    assert result.exit_code == 0
    assert "--output" in result.output


def test_cli_translate_help():
    """translate subcommand shows help."""
    runner = CliRunner()
    result = runner.invoke(main, ["translate", "--help"])
    assert result.exit_code == 0
    assert "--source" in result.output


def test_cli_patch_help():
    """patch subcommand shows help."""
    runner = CliRunner()
    result = runner.invoke(main, ["patch", "--help"])
    assert result.exit_code == 0
    assert "--source" in result.output


def test_cli_apply_help():
    """apply subcommand shows help."""
    runner = CliRunner()
    result = runner.invoke(main, ["apply", "--help"])
    assert result.exit_code == 0
    assert "--install" in result.output


def test_cli_bundle_help():
    """bundle subcommand shows help."""
    runner = CliRunner()
    result = runner.invoke(main, ["bundle", "--help"])
    assert result.exit_code == 0
    assert "--output" in result.output


def test_cli_revert_help():
    """revert subcommand shows help."""
    runner = CliRunner()
    result = runner.invoke(main, ["revert", "--help"])
    assert result.exit_code == 0
    assert "--install" in result.output


def test_cli_translate_source_not_found():
    """translate exits with error when source directory doesn't exist."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["translate", "--source", "/nonexistent/path/that/does/not/exist"],
    )
    assert result.exit_code != 0


def test_cli_patch_source_not_found():
    """patch exits with error when source directory doesn't exist."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["patch", "--source", "/nonexistent/path/that/does/not/exist"],
    )
    assert result.exit_code != 0


def test_cli_apply_source_not_found():
    """apply exits with error when install has no data/english."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["apply", "--install", "/nonexistent/path"],
    )
    assert result.exit_code != 0


def test_cli_revert_no_backup():
    """revert exits with error when no backup exists."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmp:
        # Create an install dir without backup
        install_dir = Path(tmp) / "install"
        install_dir.mkdir()
        result = runner.invoke(
            main, ["revert", "--install", str(install_dir)]
        )
        assert result.exit_code != 0
        assert "Backup" in result.output


def test_cli_apply_and_revert(tmp_path: Path):
    """apply patches English files, revert restores them."""
    # Set up a mock Exile-UI installation
    install = tmp_path / "exile-ui"
    english_dir = install / "data" / "english"
    english_dir.mkdir(parents=True)

    original_content = '\tKEY_ONE\t=\t"Hello"\n\tKEY_TWO\t=\t"World"\n'
    ui_path = english_dir / "UI.txt"
    ui_path.write_text(original_content, encoding="utf-8")

    # Create a real patch that changes KEY_ONE
    orig = parse_txt(original_content)
    translated = dict(orig)
    translated["KEY_ONE"] = "Hola"
    patch_data = generate_patch(orig, translated)

    # Save patch where the CLI expects it
    import exile_ui_es.cli as cli_mod

    cli_mod.PATCHES_DIR = tmp_path / "patches"
    cli_mod.PATCHES_DIR.mkdir(parents=True)
    save_patch(patch_data, cli_mod.PATCHES_DIR / "UI.txt.patch.json")

    # Also adjust DATA_DIR for Spanish JSON step
    cli_mod.DATA_DIR = tmp_path / "data"
    (cli_mod.DATA_DIR / "spanish").mkdir(parents=True)

    runner = CliRunner()

    # Apply the patch
    result = runner.invoke(main, ["apply", "--install", str(install)])
    assert result.exit_code == 0
    assert "Backup" in result.output
    assert "UI.txt" in result.output

    # Verify English file was patched
    patched = parse_txt(ui_path.read_text(encoding="utf-8"))
    assert patched["KEY_ONE"] == "Hola"
    assert patched["KEY_TWO"] == "World"

    # Verify backup exists with original content
    backup_path = english_dir.parent / "english.backup" / "UI.txt"
    assert backup_path.exists()
    backup = parse_txt(backup_path.read_text(encoding="utf-8"))
    assert backup["KEY_ONE"] == "Hello"

    # Revert
    result = runner.invoke(main, ["revert", "--install", str(install)])
    assert result.exit_code == 0

    # Verify restoration
    restored = parse_txt(ui_path.read_text(encoding="utf-8"))
    assert restored["KEY_ONE"] == "Hello"
    assert restored["KEY_TWO"] == "World"