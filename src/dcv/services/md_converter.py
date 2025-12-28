"""Markdown to PDF conversion handler using Playwright."""

import asyncio
import logging
import re
from importlib import resources
from pathlib import Path
from typing import Any

from jinja2 import Template
from markdown_it import MarkdownIt
from playwright.async_api import async_playwright

from dcv.errors import ConversionError
from dcv.protocols.converter_protocol import ConverterProtocol


class PlaywrightNotInstalledError(Exception):
    """Raised when Playwright browsers are not installed."""

    pass


class MdConverter(ConverterProtocol):
    """Handler for converting Markdown files to PDF using Playwright."""

    SUPPORTED_EXTENSIONS = {".md", ".markdown"}

    def __init__(
        self,
        template_path: Path | None = None,
    ) -> None:
        """
        Initialize the Markdown converter.

        Args:
            template_path: Optional custom HTML template path.
        """
        self._template_path = template_path
        self._md = MarkdownIt("commonmark", {"html": True, "breaks": True})

    def _load_assets(self, css_path: Path | None = None) -> tuple[str, str]:
        """
        Load HTML template and CSS from package assets or custom paths.

        Args:
            css_path: Optional custom CSS stylesheet path.

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
        if css_path:
            css_content = css_path.read_text(encoding="utf-8")
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

    def _render_html(self, markdown_content: str, css_path: Path | None = None) -> str:
        """
        Render Markdown to full HTML with template and styling.

        Args:
            markdown_content: Raw Markdown text.
            css_path: Optional custom CSS stylesheet path.

        Returns:
            Complete HTML document string.
        """
        # Parse Markdown to HTML
        html_body = self._md.render(markdown_content)

        # Load assets
        template_str, css_str = self._load_assets(css_path)

        # Render template
        template = Template(template_str)
        full_html = template.render(body_content=html_body, css_content=css_str)

        return full_html

    async def _convert_async(
        self,
        input_path: Path,
        output_path: Path,
        css_path: Path | None = None,
        margin_top: str | None = None,
        margin_right: str | None = None,
        margin_bottom: str | None = None,
        margin_left: str | None = None,
    ) -> None:
        """
        Async implementation of Markdown to PDF conversion.

        Args:
            input_path: Path to the source Markdown file.
            output_path: Path where the PDF file will be written.
            css_path: Optional custom CSS file path.
            margin_top: Optional top margin (e.g., "35mm").
            margin_right: Optional right margin.
            margin_bottom: Optional bottom margin.
            margin_left: Optional left margin.

        Raises:
            ConversionError: If conversion fails.
        """
        # Validate margin formats if provided
        if any([margin_top, margin_right, margin_bottom, margin_left]):
            self._validate_margins(margin_top, margin_right, margin_bottom, margin_left)

        # Read Markdown content
        md_content = input_path.read_text(encoding="utf-8")

        # Render to HTML
        full_html = self._render_html(md_content, css_path)

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

                # Build PDF options
                pdf_options: dict[str, Any] = {
                    "path": str(output_path),
                    "prefer_css_page_size": True,  # Always honor CSS @page rules
                    "print_background": True,
                }

                # If CLI margins provided, they override CSS
                if any([margin_top, margin_right, margin_bottom, margin_left]):
                    pdf_options["margin"] = {}
                    if margin_top:
                        pdf_options["margin"]["top"] = margin_top
                    if margin_right:
                        pdf_options["margin"]["right"] = margin_right
                    if margin_bottom:
                        pdf_options["margin"]["bottom"] = margin_bottom
                    if margin_left:
                        pdf_options["margin"]["left"] = margin_left

                # Generate PDF
                await page.pdf(**pdf_options)

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

    def _validate_margins(
        self,
        margin_top: str | None,
        margin_right: str | None,
        margin_bottom: str | None,
        margin_left: str | None,
    ) -> None:
        """
        Validate margin format strings.

        Args:
            margin_top: Top margin specification.
            margin_right: Right margin specification.
            margin_bottom: Bottom margin specification.
            margin_left: Left margin specification.

        Raises:
            ValueError: If any margin has invalid format.
        """
        margin_pattern = re.compile(r"^\d+(\.\d+)?(mm|cm|in|px|pt)$")
        margins = {
            "top": margin_top,
            "right": margin_right,
            "bottom": margin_bottom,
            "left": margin_left,
        }

        for name, value in margins.items():
            if value and not margin_pattern.match(value):
                raise ValueError(
                    f"Invalid margin format for {name}: '{value}'. "
                    f"Expected format: <number><unit> (e.g., '30mm', '1.5in', '20pt')"
                )

    def convert(
        self,
        input_path: Path,
        output_path: Path,
        **kwargs: Any,
    ) -> None:
        """
        Convert a Markdown file to PDF.

        Args:
            input_path: Path to the source Markdown file.
            output_path: Path where the PDF file will be written.
            **kwargs: Optional conversion settings:
                - css_path (Path): Custom CSS file path
                - margin_top (str): Top margin (e.g., "35mm")
                - margin_right (str): Right margin
                - margin_bottom (str): Bottom margin
                - margin_left (str): Left margin

        Raises:
            FileNotFoundError: If input file does not exist.
            PlaywrightNotInstalledError: If Playwright browsers are not installed.
            ConversionError: If conversion fails.
            ValueError: If margin formats are invalid.
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        if not self.supports_extension(input_path.suffix):
            raise ConversionError(
                f"Unsupported file extension: {input_path.suffix}. "
                f"Supported: {self.SUPPORTED_EXTENSIONS}"
            )

        # Extract kwargs
        css_path = kwargs.get("css_path")
        margin_top = kwargs.get("margin_top")
        margin_right = kwargs.get("margin_right")
        margin_bottom = kwargs.get("margin_bottom")
        margin_left = kwargs.get("margin_left")

        # Run async conversion in sync context
        asyncio.run(
            self._convert_async(
                input_path,
                output_path,
                css_path=css_path,
                margin_top=margin_top,
                margin_right=margin_right,
                margin_bottom=margin_bottom,
                margin_left=margin_left,
            )
        )

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
