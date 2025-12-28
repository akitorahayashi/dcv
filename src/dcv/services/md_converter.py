"""Markdown to PDF conversion handler using Playwright."""

import asyncio
import logging
from importlib import resources
from pathlib import Path

from jinja2 import Template
from markdown_it import MarkdownIt
from playwright.async_api import async_playwright

from dcv.errors import ConversionError
from dcv.protocols.converter_protocol import ConverterProtocol

# PDF generation constants
PDF_FORMAT = "A4"
PDF_MARGIN_TOP = "30mm"
PDF_MARGIN_RIGHT = "20mm"
PDF_MARGIN_BOTTOM = "30mm"  # Matches original md-to-pdf config
PDF_MARGIN_LEFT = "20mm"
PDF_SCALE = 1.0


class PlaywrightNotInstalledError(Exception):
    """Raised when Playwright browsers are not installed."""

    pass


class MdConverter(ConverterProtocol):
    """Handler for converting Markdown files to PDF using Playwright."""

    SUPPORTED_EXTENSIONS = {".md", ".markdown"}

    def __init__(
        self,
        template_path: Path | None = None,
        css_path: Path | None = None,
    ) -> None:
        """
        Initialize the Markdown converter.

        Args:
            template_path: Optional custom HTML template path.
            css_path: Optional custom CSS stylesheet path.
        """
        self._template_path = template_path
        self._css_path = css_path
        self._md = MarkdownIt("commonmark", {"html": True, "breaks": True})

    def _load_assets(self) -> tuple[str, str]:
        """
        Load HTML template and CSS from package assets or custom paths.

        Returns:
            Tuple of (template_content, css_content).

        Raises:
            FileNotFoundError: If custom paths provided but files don't exist.
        """
        # Load template
        if self._template_path:
            template_content = self._template_path.read_text(encoding="utf-8")
        else:
            try:
                with resources.as_file(
                    resources.files("dcv.assets.templates").joinpath("base.html.jinja")
                ) as template_file:
                    template_content = Path(template_file).read_text(encoding="utf-8")
            except (TypeError, FileNotFoundError):
                # Fallback for development
                fallback_path = (
                    Path(__file__).parent.parent
                    / "assets"
                    / "templates"
                    / "base.html.jinja"
                )
                template_content = fallback_path.read_text(encoding="utf-8")

        # Load CSS
        if self._css_path:
            css_content = self._css_path.read_text(encoding="utf-8")
        else:
            try:
                with resources.as_file(
                    resources.files("dcv.assets.styles").joinpath("pdf.css")
                ) as css_file:
                    css_content = Path(css_file).read_text(encoding="utf-8")
            except (TypeError, FileNotFoundError):
                # Fallback for development
                fallback_path = (
                    Path(__file__).parent.parent / "assets" / "styles" / "pdf.css"
                )
                css_content = fallback_path.read_text(encoding="utf-8")

        return template_content, css_content

    def _render_html(self, markdown_content: str) -> str:
        """
        Render Markdown to full HTML with template and styling.

        Args:
            markdown_content: Raw Markdown text.

        Returns:
            Complete HTML document string.
        """
        # Parse Markdown to HTML
        html_body = self._md.render(markdown_content)

        # Load assets
        template_str, css_str = self._load_assets()

        # Render template
        template = Template(template_str)
        full_html = template.render(body_content=html_body, css_content=css_str)

        return full_html

    async def _convert_async(self, input_path: Path, output_path: Path) -> None:
        """
        Async implementation of Markdown to PDF conversion.

        Args:
            input_path: Path to the source Markdown file.
            output_path: Path where the PDF file will be written.

        Raises:
            ConversionError: If conversion fails.
        """
        # Read Markdown content
        md_content = input_path.read_text(encoding="utf-8")

        # Render to HTML
        full_html = self._render_html(md_content)

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            async with async_playwright() as p:
                # Launch browser
                browser = await p.chromium.launch()
                page = await browser.new_page()

                # Set content and wait for network idle
                await page.set_content(full_html, wait_until="networkidle")

                # Wait for MathJax to finish rendering
                try:
                    await page.evaluate("window.MathJax.typesetPromise()")
                except Exception as e:
                    # MathJax might not be needed for all documents, but log the error for debugging
                    logging.warning(f"Could not typeset MathJax: {e}")

                # Generate PDF with settings matching md-to-pdf config
                await page.pdf(
                    path=str(output_path),
                    format=PDF_FORMAT,
                    margin={
                        "top": PDF_MARGIN_TOP,
                        "right": PDF_MARGIN_RIGHT,
                        "bottom": PDF_MARGIN_BOTTOM,
                        "left": PDF_MARGIN_LEFT,
                    },
                    print_background=True,
                    scale=PDF_SCALE,
                )

                await browser.close()

        except Exception as e:
            error_msg = str(e)
            if (
                "Executable doesn't exist" in error_msg
                or "browser" in error_msg.lower()
            ):
                raise PlaywrightNotInstalledError(
                    "Playwright browsers not installed. Please run:\n"
                    "  playwright install chromium"
                ) from e
            raise ConversionError(f"PDF generation failed: {error_msg}") from e

    def convert(self, input_path: Path, output_path: Path) -> None:
        """
        Convert a Markdown file to PDF.

        Args:
            input_path: Path to the source Markdown file.
            output_path: Path where the PDF file will be written.

        Raises:
            FileNotFoundError: If input file does not exist.
            PlaywrightNotInstalledError: If Playwright browsers are not installed.
            ConversionError: If conversion fails.
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        if not self.supports_extension(input_path.suffix):
            raise ConversionError(
                f"Unsupported file extension: {input_path.suffix}. "
                f"Supported: {self.SUPPORTED_EXTENSIONS}"
            )

        # Run async conversion in sync context
        asyncio.run(self._convert_async(input_path, output_path))

    def supports_extension(self, extension: str) -> bool:
        """
        Check if this converter supports the given file extension.

        Args:
            extension: File extension (e.g., '.md').

        Returns:
            True if the extension is supported.
        """
        return extension.lower() in self.SUPPORTED_EXTENSIONS


_: ConverterProtocol = MdConverter()
