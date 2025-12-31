"""Integration tests for basic CLI command interface."""

from typer.testing import CliRunner

from dcv.main import app


class TestCLICommands:
    """Tests for basic CLI command functionality."""

    def test_version_flag_shows_version(self, cli_runner: CliRunner):
        """Test that --version flag shows version information."""
        result = cli_runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert "dcv version:" in result.output

    def test_help_flag_shows_help(self, cli_runner: CliRunner):
        """Test that --help flag shows help information."""
        result = cli_runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "dcv" in result.output
        assert "pdf2md" in result.output
        assert "md2pdf" in result.output

    def test_no_args_shows_help(self, cli_runner: CliRunner):
        """Test that running without arguments shows help (exit code 0 or 2)."""
        result = cli_runner.invoke(app, [])

        assert "Usage:" in result.output or "dcv" in result.output

    def test_pdf2md_help(self, cli_runner: CliRunner):
        """Test that pdf2md --help shows command help."""
        result = cli_runner.invoke(app, ["pdf2md", "--help"])

        assert result.exit_code == 0
        assert "PATH" in result.output
        assert "-o" in result.output or "--output-dir" in result.output

    def test_md2pdf_help(self, cli_runner: CliRunner):
        """Test that md2pdf --help shows command help."""
        result = cli_runner.invoke(app, ["md2pdf", "--help"])

        assert result.exit_code == 0
        assert "PATH" in result.output
        assert "-o" in result.output or "--output-dir" in result.output

    def test_pdf2md_requires_input(self, cli_runner: CliRunner):
        """Test that pdf2md requires PATH argument."""
        result = cli_runner.invoke(app, ["pdf2md"])

        assert result.exit_code != 0
        assert "Missing argument" in result.output or "PATH" in result.output

    def test_md2pdf_requires_input(self, cli_runner: CliRunner):
        """Test that md2pdf requires PATH argument."""
        result = cli_runner.invoke(app, ["md2pdf"])

        assert result.exit_code != 0
        assert "Missing argument" in result.output or "PATH" in result.output
