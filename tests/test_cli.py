# tests/test_cli.py
from click.testing import CliRunner

from exile_ui_es.cli import main


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