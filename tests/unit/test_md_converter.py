"""Unit tests for the Markdown to PDF handler service."""

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
        """Test that custom template path can be provided."""
        custom_template = tmp_path / "template.html"
        custom_template.write_text("<html><body>{{ body_content }}</body></html>")

        handler = MdConverter(template_path=custom_template)
        assert handler._template_path == custom_template

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

    def test_convert_with_custom_css(
        self,
        tmp_path: Path,
    ):
        """Test conversion with custom CSS file."""
        from unittest.mock import AsyncMock, MagicMock, patch

        # Set up async mock structure
        with patch("dcv.services.md_converter.async_playwright") as mock_playwright:
            mock_p = MagicMock()
            mock_browser = MagicMock()
            mock_page = MagicMock()

            mock_playwright.return_value.__aenter__ = AsyncMock(return_value=mock_p)
            mock_playwright.return_value.__aexit__ = AsyncMock()

            mock_p.chromium.launch = AsyncMock(return_value=mock_browser)
            mock_browser.new_page = AsyncMock(return_value=mock_page)
            mock_browser.close = AsyncMock()

            mock_page.set_content = AsyncMock()
            mock_page.evaluate = AsyncMock()
            mock_page.pdf = AsyncMock()

            handler = MdConverter()

            input_path = tmp_path / "document.md"
            input_path.write_text("# Test Document")
            output_path = tmp_path / "output.pdf"

            custom_css = tmp_path / "custom.css"
            custom_css.write_text("@page { size: A4; margin: 40mm; }")

            handler.convert(input_path, output_path, css_path=custom_css)

            # Verify pdf was called with prefer_css_page_size
            mock_page.pdf.assert_called_once()
            call_kwargs = mock_page.pdf.call_args.kwargs
            assert call_kwargs["prefer_css_page_size"] is True
            assert "margin" not in call_kwargs  # No CLI margins provided

    def test_convert_with_margin_overrides(
        self,
        tmp_path: Path,
    ):
        """Test conversion with margin CLI overrides."""
        from unittest.mock import AsyncMock, MagicMock, patch

        with patch("dcv.services.md_converter.async_playwright") as mock_playwright:
            mock_p = MagicMock()
            mock_browser = MagicMock()
            mock_page = MagicMock()

            mock_playwright.return_value.__aenter__ = AsyncMock(return_value=mock_p)
            mock_playwright.return_value.__aexit__ = AsyncMock()

            mock_p.chromium.launch = AsyncMock(return_value=mock_browser)
            mock_browser.new_page = AsyncMock(return_value=mock_page)
            mock_browser.close = AsyncMock()

            mock_page.set_content = AsyncMock()
            mock_page.evaluate = AsyncMock()
            mock_page.pdf = AsyncMock()

            handler = MdConverter()

            input_path = tmp_path / "document.md"
            input_path.write_text("# Test Document")
            output_path = tmp_path / "output.pdf"

            handler.convert(
                input_path,
                output_path,
                margin_top="35mm",
                margin_bottom="30mm",
            )

            # Verify margins were passed
            mock_page.pdf.assert_called_once()
            call_kwargs = mock_page.pdf.call_args.kwargs
            assert call_kwargs["prefer_css_page_size"] is True
            assert "margin" in call_kwargs
            assert call_kwargs["margin"]["top"] == "35mm"
            assert call_kwargs["margin"]["bottom"] == "30mm"

    def test_convert_with_invalid_margin_format(self, tmp_path: Path):
        """Test that invalid margin format raises ValueError."""
        handler = MdConverter()

        input_path = tmp_path / "document.md"
        input_path.write_text("# Test Document")
        output_path = tmp_path / "output.pdf"

        with pytest.raises(ValueError, match="Invalid margin format"):
            handler.convert(
                input_path,
                output_path,
                margin_top="invalid",
            )

        with pytest.raises(ValueError, match="Invalid margin format"):
            handler.convert(
                input_path,
                output_path,
                margin_left="30",  # Missing unit
            )

    def test_margin_validation(self):
        """Test margin validation logic."""
        handler = MdConverter()

        # Valid formats
        handler._validate_margins("30mm", "20mm", "30mm", "20mm")
        handler._validate_margins("1.5in", "1in", "2.5cm", "10pt")
        handler._validate_margins(None, "20mm", None, None)

        # Invalid formats
        with pytest.raises(ValueError, match="Invalid margin format"):
            handler._validate_margins("invalid", None, None, None)

        with pytest.raises(ValueError, match="Invalid margin format"):
            handler._validate_margins(None, "30", None, None)  # Missing unit

        with pytest.raises(ValueError, match="Invalid margin format"):
            handler._validate_margins(None, None, "30 mm", None)  # Space not allowed
