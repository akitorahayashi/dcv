"""Unit tests for the PDF handler service."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from dcv.services.pdf_handler import ConversionError, PdfHandler


class TestPdfHandler:
    """Unit tests for PdfHandler."""

    def test_supports_extension_pdf(self):
        """Test that .pdf extension is supported."""
        handler = PdfHandler()
        assert handler.supports_extension(".pdf") is True
        assert handler.supports_extension(".PDF") is True

    def test_supports_extension_unsupported(self):
        """Test that unsupported extensions return False."""
        handler = PdfHandler()
        assert handler.supports_extension(".md") is False
        assert handler.supports_extension(".txt") is False
        assert handler.supports_extension(".docx") is False

    def test_convert_file_not_found(self, tmp_path: Path):
        """Test that FileNotFoundError is raised for missing input."""
        handler = PdfHandler()
        input_path = tmp_path / "nonexistent.pdf"
        output_path = tmp_path / "output.md"

        with pytest.raises(FileNotFoundError, match="Input file not found"):
            handler.convert(input_path, output_path)

    def test_convert_unsupported_extension(self, tmp_path: Path):
        """Test that ConversionError is raised for unsupported file types."""
        handler = PdfHandler()
        input_path = tmp_path / "document.txt"
        input_path.write_text("test content")
        output_path = tmp_path / "output.md"

        with pytest.raises(ConversionError, match="Unsupported file extension"):
            handler.convert(input_path, output_path)

    @patch("dcv.services.pdf_handler.MarkItDown")
    def test_convert_success(self, mock_md_class: MagicMock, tmp_path: Path):
        """Test successful PDF to Markdown conversion."""
        # Setup mock
        mock_md_instance = MagicMock()
        mock_md_class.return_value = mock_md_instance
        mock_result = MagicMock()
        mock_result.text_content = "# Converted Content\n\nThis is the converted text."
        mock_md_instance.convert.return_value = mock_result

        handler = PdfHandler()

        input_path = tmp_path / "document.pdf"
        input_path.write_bytes(b"%PDF-1.4 dummy content")
        output_path = tmp_path / "output" / "document.md"

        handler.convert(input_path, output_path)

        # Verify
        mock_md_instance.convert.assert_called_once_with(str(input_path))
        assert output_path.exists()
        assert output_path.read_text() == "# Converted Content\n\nThis is the converted text."

    @patch("dcv.services.pdf_handler.MarkItDown")
    def test_convert_creates_output_directory(self, mock_md_class: MagicMock, tmp_path: Path):
        """Test that output directory is created if it doesn't exist."""
        mock_md_instance = MagicMock()
        mock_md_class.return_value = mock_md_instance
        mock_result = MagicMock()
        mock_result.text_content = "Test content"
        mock_md_instance.convert.return_value = mock_result

        handler = PdfHandler()

        input_path = tmp_path / "document.pdf"
        input_path.write_bytes(b"%PDF-1.4 dummy content")
        output_path = tmp_path / "nested" / "deep" / "output.md"

        handler.convert(input_path, output_path)

        assert output_path.parent.exists()
        assert output_path.exists()

    @patch("dcv.services.pdf_handler.MarkItDown")
    def test_convert_handles_conversion_error(self, mock_md_class: MagicMock, tmp_path: Path):
        """Test that conversion errors are wrapped properly."""
        mock_md_instance = MagicMock()
        mock_md_class.return_value = mock_md_instance
        mock_md_instance.convert.side_effect = RuntimeError("MarkItDown internal error")

        handler = PdfHandler()

        input_path = tmp_path / "document.pdf"
        input_path.write_bytes(b"%PDF-1.4 dummy content")
        output_path = tmp_path / "output.md"

        with pytest.raises(ConversionError, match="Failed to convert"):
            handler.convert(input_path, output_path)
