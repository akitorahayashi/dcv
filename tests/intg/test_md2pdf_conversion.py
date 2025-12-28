"""Integration tests for Markdown to PDF conversion."""

import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from dcv.main import app

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


class TestMd2PdfCLI:
    """Integration tests for md2pdf CLI command."""

    @patch("dcv.services.md_converter.shutil.which")
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

        assert "md-to-pdf" in result.output.lower()


class TestMd2PdfRealConversion:
    """Integration tests using real fixture files without mocks."""

    @pytest.mark.skipif(
        shutil.which("md-to-pdf") is None, reason="md-to-pdf not installed"
    )
    def test_md2pdf_real_conversion_no_errors(
        self, cli_runner: CliRunner, tmp_path: Path
    ):
        """Test MD→PDF conversion completes without errors using sample.md fixture."""
        sample_md = FIXTURES_DIR / "sample.md"
        output_dir = tmp_path / "output"
        result = cli_runner.invoke(
            app, ["md2pdf", "-f", str(sample_md), "-o", str(output_dir)]
        )

        assert result.exit_code == 0
        assert "Converting:" in result.output

        output_file = output_dir / "sample.pdf"
        assert output_file.exists(), (
            f"Output file not created. CLI output:\n{result.output}"
        )

        with output_file.open("rb") as f:
            header = f.read(4)
            assert header == b"%PDF"
