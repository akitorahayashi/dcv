"""Integration tests for PDF to Markdown conversion."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from dcv.main import app

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


class TestPdf2MdCLI:
    """Integration tests for pdf2md CLI command."""

    @patch("dcv.services.pdf_converter.PdfConverter.convert")
    def test_pdf2md_with_file(
        self, mock_convert: MagicMock, cli_runner: CliRunner, tmp_path: Path
    ):
        """Test pdf2md command with a file input."""
        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_bytes(b"%PDF-1.4 test content")

        result = cli_runner.invoke(
            app, ["pdf2md", "-f", str(test_pdf), "-o", str(tmp_path / "output")]
        )

        assert result.exit_code == 0 and "Converting:" in result.output

    @patch("dcv.services.pdf_converter.PdfConverter.convert")
    def test_pdf2md_with_directory(
        self, mock_convert: MagicMock, cli_runner: CliRunner, tmp_path: Path
    ):
        """Test pdf2md command with a directory input."""
        input_dir = tmp_path / "pdfs"
        input_dir.mkdir()
        (input_dir / "doc1.pdf").write_bytes(b"%PDF-1.4 test")
        (input_dir / "doc2.pdf").write_bytes(b"%PDF-1.4 test")

        result = cli_runner.invoke(
            app, ["pdf2md", "-d", str(input_dir), "-o", str(tmp_path / "output")]
        )

        assert result.exit_code == 0 and "Converting:" in result.output


class TestPdf2MdRealConversion:
    """Integration tests using real fixture files without mocks."""

    def test_pdf2md_real_conversion_no_errors(
        self, cli_runner: CliRunner, tmp_path: Path
    ):
        """Test PDF→MD conversion completes without errors via MD→PDF→MD round-trip."""
        sample_md = FIXTURES_DIR / "sample.md"

        # First: MD→PDF
        pdf_dir = tmp_path / "pdf"
        result = cli_runner.invoke(
            app, ["md2pdf", "-f", str(sample_md), "-o", str(pdf_dir)]
        )
        assert result.exit_code == 0

        # Then: PDF→MD
        sample_pdf = pdf_dir / "sample.pdf"
        output_dir = tmp_path / "output"
        result = cli_runner.invoke(
            app, ["pdf2md", "-f", str(sample_pdf), "-o", str(output_dir)]
        )

        assert result.exit_code == 0
        assert "Converting:" in result.output

        output_file = output_dir / "sample.md"
        assert output_file.exists(), (
            f"Output file not created. CLI output:\n{result.output}"
        )

        content = output_file.read_text(encoding="utf-8")
        assert "サンプルドキュメント" in content
        assert "dcv" in content
