"""Protocol definitions for converter services."""

from pathlib import Path
from typing import Any, Protocol


class ConverterProtocol(Protocol):
    """Protocol for document conversion services."""

    def convert(self, input_path: Path, output_path: Path, **kwargs: Any) -> None:
        """
        Convert a document from input path to output path.

        Args:
            input_path: Path to the source file.
            output_path: Path where the converted file will be written.
            **kwargs: Additional conversion options (e.g., css_path, margins).

        Raises:
            FileNotFoundError: If input file does not exist.
            ConversionError: If conversion fails.
        """
        ...

    def supports_extension(self, extension: str) -> bool:
        """
        Check if this converter supports the given file extension.

        Args:
            extension: File extension (e.g., '.pdf', '.md').

        Returns:
            True if the extension is supported.
        """
        ...
