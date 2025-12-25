"""PDF to Markdown conversion handler using markitdown."""

from pathlib import Path

from markitdown import MarkItDown

from dcv.errors import ConversionError
from dcv.protocols.converter_protocol import ConverterProtocol


class PdfHandler(ConverterProtocol):
    """Handler for converting PDF files to Markdown using markitdown."""

    SUPPORTED_EXTENSIONS = {".pdf"}

    def __init__(self) -> None:
        """Initialize the PDF handler with a MarkItDown instance."""
        self._md = MarkItDown()

    def convert(self, input_path: Path, output_path: Path) -> None:
        """
        Convert a PDF file to Markdown.

        Args:
            input_path: Path to the source PDF file.
            output_path: Path where the Markdown file will be written.

        Raises:
            FileNotFoundError: If input file does not exist.
            ConversionError: If conversion fails.
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        if not self.supports_extension(input_path.suffix):
            raise ConversionError(
                f"Unsupported file extension: {input_path.suffix}. "
                f"Supported: {self.SUPPORTED_EXTENSIONS}"
            )

        try:
            result = self._md.convert(str(input_path))
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(result.text_content, encoding="utf-8")
        except Exception as e:
            raise ConversionError(f"Failed to convert {input_path}: {e}") from e

    def supports_extension(self, extension: str) -> bool:
        """
        Check if this converter supports the given file extension.

        Args:
            extension: File extension (e.g., '.pdf').

        Returns:
            True if the extension is supported.
        """
        return extension.lower() in self.SUPPORTED_EXTENSIONS


_: ConverterProtocol = PdfHandler()
