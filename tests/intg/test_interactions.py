"""Integration tests for CLI command interactions."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from dcv.main import app


class TestCLIIntegration:
    """Integration tests for CLI command interactions."""

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
        assert "--file" in result.output
        assert "--dir" in result.output
        assert "--output-dir" in result.output

    def test_md2pdf_help(self, cli_runner: CliRunner):
        """Test that md2pdf --help shows command help."""
        result = cli_runner.invoke(app, ["md2pdf", "--help"])

        assert result.exit_code == 0
        assert "--file" in result.output
        assert "--dir" in result.output
        assert "--output-dir" in result.output

    def test_pdf2md_requires_input(self, cli_runner: CliRunner):
        """Test that pdf2md requires either --file or --dir."""
        result = cli_runner.invoke(app, ["pdf2md"])

        assert result.exit_code != 0
        assert "must be specified" in result.output or "Error" in result.output

    def test_md2pdf_requires_input(self, cli_runner: CliRunner):
        """Test that md2pdf requires either --file or --dir."""
        result = cli_runner.invoke(app, ["md2pdf"])

        assert result.exit_code != 0
        assert "must be specified" in result.output or "Error" in result.output

    @patch("dcv.services.pdf_handler.PdfHandler.convert")
    def test_pdf2md_with_file(
        self, mock_convert: MagicMock, cli_runner: CliRunner, tmp_path: Path
    ):
        """Test pdf2md command with a file input."""
        # Create a test PDF file
        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_bytes(b"%PDF-1.4 test content")

        result = cli_runner.invoke(
            app, ["pdf2md", "-f", str(test_pdf), "-o", str(tmp_path / "output")]
        )

        # The command should run without errors (mocked conversion)
        assert result.exit_code == 0 and "Converting:" in result.output

    @patch("dcv.services.pdf_handler.PdfHandler.convert")
    def test_pdf2md_with_directory(
        self, mock_convert: MagicMock, cli_runner: CliRunner, tmp_path: Path
    ):
        """Test pdf2md command with a directory input."""
        # Create test PDF files
        input_dir = tmp_path / "pdfs"
        input_dir.mkdir()
        (input_dir / "doc1.pdf").write_bytes(b"%PDF-1.4 test")
        (input_dir / "doc2.pdf").write_bytes(b"%PDF-1.4 test")

        result = cli_runner.invoke(
            app, ["pdf2md", "-d", str(input_dir), "-o", str(tmp_path / "output")]
        )

        # Should process both files
        assert result.exit_code == 0 and "Converting:" in result.output

    @patch("dcv.services.md_handler.shutil.which")
    def test_md2pdf_without_md_to_pdf_installed(
        self, mock_which: MagicMock, cli_runner: CliRunner, tmp_path: Path
    ):
        """Test md2pdf shows error when md-to-pdf is not installed."""
        mock_which.return_value = None

        test_md = tmp_path / "test.md"
        test_md.write_text("# Test Document")

        result = cli_runner.invoke(
            app, ["md2pdf", "-f", str(test_md), "-o", str(tmp_path / "output")]
        )

        # Should show an error about md-to-pdf not being installed
        assert "md-to-pdf" in result.output.lower()


class TestContainerIntegration:
    """Integration tests for the DI container."""

    def test_container_initializes_with_defaults(self, cli_runner: CliRunner):
        """Test that the container initializes correctly."""
        result = cli_runner.invoke(app, ["--version"])

        # If version runs, container initialized correctly
        assert result.exit_code == 0
        assert "dcv" in result.output
