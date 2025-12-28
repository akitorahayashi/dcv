"""Unit tests for the Markdown to PDF handler service."""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from dcv.errors import ConversionError
from dcv.services import MdConverter

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


class TestMdConverter:
    """Unit tests for MdConverter."""

    def test_supports_extension_md(self):
        """Test that .md extension is supported."""
        handler = MdConverter()
        assert handler.supports_extension(".md") is True
        assert handler.supports_extension(".MD") is True
        assert handler.supports_extension(".markdown") is True

    def test_supports_extension_unsupported(self):
        """Test that unsupported extensions return False."""
        handler = MdConverter()
        assert handler.supports_extension(".pdf") is False
        assert handler.supports_extension(".txt") is False
        assert handler.supports_extension(".docx") is False

    def test_convert_file_not_found(self, tmp_path: Path):
        """Test that FileNotFoundError is raised for missing input."""
        handler = MdConverter()
        input_path = tmp_path / "nonexistent.md"
        output_path = tmp_path / "output.pdf"

        with pytest.raises(FileNotFoundError, match="Input file not found"):
            handler.convert(input_path, output_path)

    def test_convert_unsupported_extension(self, tmp_path: Path):
        """Test that ConversionError is raised for unsupported file types."""
        handler = MdConverter()
        input_path = tmp_path / "document.txt"
        input_path.write_text("test content")
        output_path = tmp_path / "output.pdf"

        with pytest.raises(ConversionError, match="Unsupported file extension"):
            handler.convert(input_path, output_path)

    # Note: Async mocking is complex. Integration tests cover error scenarios.
    # These unit tests focus on synchronous methods and basic flows.

    @patch("dcv.services.md_converter.async_playwright")
    def test_convert_success(
        self,
        mock_playwright: MagicMock,
        tmp_path: Path,
    ):
        """Test successful Markdown to PDF conversion."""
        # Set up async mock structure
        mock_p = MagicMock()
        mock_browser = MagicMock()
        mock_page = MagicMock()

        # Mock async context manager
        mock_playwright.return_value.__aenter__ = AsyncMock(return_value=mock_p)
        mock_playwright.return_value.__aexit__ = AsyncMock()

        # Mock browser launch and page creation
        mock_p.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_browser.close = AsyncMock()

        # Mock page methods
        mock_page.set_content = AsyncMock()
        mock_page.evaluate = AsyncMock()
        mock_page.pdf = AsyncMock()

        handler = MdConverter()

        input_path = tmp_path / "document.md"
        input_path.write_text("# Test Document\n\nThis is a test.")
        output_path = tmp_path / "output" / "document.pdf"

        handler.convert(input_path, output_path)

        # Verify page methods were called
        mock_page.set_content.assert_called_once()
        mock_page.pdf.assert_called_once()
        mock_browser.close.assert_called_once()

        # Verify output directory was created
        assert output_path.parent.exists()

    def test_custom_template_and_css_paths(self, tmp_path: Path):
        """Test that custom template and CSS paths can be provided."""
        custom_template = tmp_path / "template.html"
        custom_template.write_text("<html><body>{{ body_content }}</body></html>")

        custom_css = tmp_path / "style.css"
        custom_css.write_text("body { margin: 0; }")

        handler = MdConverter(template_path=custom_template, css_path=custom_css)
        assert handler._template_path == custom_template
        assert handler._css_path == custom_css

    def test_asset_loading(self, tmp_path: Path):
        """Test that assets are loaded correctly."""
        handler = MdConverter()

        # Should not raise an exception
        template_str, css_str = handler._load_assets()

        assert "<!DOCTYPE html>" in template_str
        assert "{{ body_content }}" in template_str
        assert "MathJax" in template_str
        assert "font-family" in css_str

    def test_render_html(self, tmp_path: Path):
        """Test HTML rendering from Markdown."""
        handler = MdConverter()

        markdown_content = "# Hello\n\nThis is a **test**."
        html = handler._render_html(markdown_content)

        assert "<h1>Hello</h1>" in html
        assert "<strong>test</strong>" in html
        assert "<!DOCTYPE html>" in html
