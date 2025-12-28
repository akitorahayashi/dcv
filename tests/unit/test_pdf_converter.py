"""Unit tests for the PDF handler service."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from dcv.errors import ConversionError
from dcv.services import PdfConverter

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


class TestPdfConverter:
    """Unit tests for PdfConverter."""

    def test_supports_extension_pdf(self):
        """Test that .pdf extension is supported."""
        handler = PdfConverter()
        assert handler.supports_extension(".pdf") is True
        assert handler.supports_extension(".PDF") is True

    def test_supports_extension_unsupported(self):
        """Test that unsupported extensions return False."""
        handler = PdfConverter()
        assert handler.supports_extension(".md") is False
        assert handler.supports_extension(".txt") is False
        assert handler.supports_extension(".docx") is False

    def test_convert_file_not_found(self, tmp_path: Path):
        """Test that FileNotFoundError is raised for missing input."""
        handler = PdfConverter()
        input_path = tmp_path / "nonexistent.pdf"
        output_path = tmp_path / "output.md"

        with pytest.raises(FileNotFoundError, match="Input file not found"):
            handler.convert(input_path, output_path)

    def test_convert_unsupported_extension(self, tmp_path: Path):
        """Test that ConversionError is raised for unsupported file types."""
        handler = PdfConverter()
        input_path = tmp_path / "document.txt"
        input_path.write_text("test content")
        output_path = tmp_path / "output.md"

        with pytest.raises(ConversionError, match="Unsupported file extension"):
            handler.convert(input_path, output_path)

    @patch("dcv.services.pdf_converter.MarkItDown")
    def test_convert_success(self, mock_md_class: MagicMock, tmp_path: Path):
        """Test successful PDF to Markdown conversion."""
        # Setup mock
        mock_md_instance = MagicMock()
        mock_md_class.return_value = mock_md_instance
        mock_result = MagicMock()
        mock_result.text_content = "# Converted Content\n\nThis is the converted text."
        mock_md_instance.convert.return_value = mock_result

        handler = PdfConverter()

        input_path = tmp_path / "document.pdf"
        input_path.write_bytes(b"%PDF-1.4 dummy content")
        output_path = tmp_path / "output" / "document.md"

        handler.convert(input_path, output_path)

        # Verify
        mock_md_instance.convert.assert_called_once_with(str(input_path))
        assert output_path.exists()
        assert (
            output_path.read_text()
            == "# Converted Content\n\nThis is the converted text."
        )

    @patch("dcv.services.pdf_converter.MarkItDown")
    def test_convert_creates_output_directory(
        self, mock_md_class: MagicMock, tmp_path: Path
    ):
        """Test that output directory is created if it doesn't exist."""
        mock_md_instance = MagicMock()
        mock_md_class.return_value = mock_md_instance
        mock_result = MagicMock()
        mock_result.text_content = "Test content"
        mock_md_instance.convert.return_value = mock_result

        handler = PdfConverter()

        input_path = tmp_path / "document.pdf"
        input_path.write_bytes(b"%PDF-1.4 dummy content")
        output_path = tmp_path / "nested" / "deep" / "output.md"

        handler.convert(input_path, output_path)

        assert output_path.parent.exists()
        assert output_path.exists()

    @patch("dcv.services.pdf_converter.MarkItDown")
    def test_convert_handles_conversion_error(
        self, mock_md_class: MagicMock, tmp_path: Path
    ):
        """Test that conversion errors are wrapped properly."""
        mock_md_instance = MagicMock()
        mock_md_class.return_value = mock_md_instance
        mock_md_instance.convert.side_effect = RuntimeError("MarkItDown internal error")

        handler = PdfConverter()

        input_path = tmp_path / "document.pdf"
        input_path.write_bytes(b"%PDF-1.4 dummy content")
        output_path = tmp_path / "output.md"

        with pytest.raises(ConversionError, match="Failed to convert"):
            handler.convert(input_path, output_path)

    def test_convert_real_pdf_fixture_no_errors(self, tmp_path: Path):
        """Test PDF→MD conversion completes without errors via MD→PDF→MD round-trip."""
        from dcv.services import MdConverter

        sample_md = FIXTURES_DIR / "sample.md"

        # First: MD→PDF
        md_converter = MdConverter()
        sample_pdf = tmp_path / "sample.pdf"
        md_converter.convert(sample_md, sample_pdf)

        # Then: PDF→MD
        pdf_converter = PdfConverter()
        output_md = tmp_path / "output.md"
        pdf_converter.convert(sample_pdf, output_md)

        assert output_md.exists()
        content = output_md.read_text(encoding="utf-8")
        assert "サンプルドキュメント" in content
        assert "dcv" in content
