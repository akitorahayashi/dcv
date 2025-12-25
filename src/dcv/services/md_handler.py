"""Markdown to PDF conversion handler using md-to-pdf."""

import shutil
import subprocess
from importlib import resources
from pathlib import Path

from dcv.protocols.converter_protocol import ConverterProtocol
from dcv.services.pdf_handler import ConversionError


class MdToPdfNotFoundError(Exception):
    """Raised when md-to-pdf command is not available."""

    pass


class MdHandler(ConverterProtocol):
    """Handler for converting Markdown files to PDF using md-to-pdf."""

    SUPPORTED_EXTENSIONS = {".md", ".markdown"}

    def __init__(self, config_path: Path | None = None) -> None:
        """
        Initialize the Markdown handler.

        Args:
            config_path: Optional custom config file path. If None, uses bundled config.
        """
        self._config_path = config_path or self._get_default_config_path()

    def _get_default_config_path(self) -> Path:
        """Get the path to the bundled md-to-pdf config file."""
        try:
            with resources.as_file(
                resources.files("dcv.assets").joinpath("md-to-pdf-config.js")
            ) as config_file:
                return Path(config_file)
        except (TypeError, FileNotFoundError):
            # Fallback for development or when package not installed
            return Path(__file__).parent.parent / "assets" / "md-to-pdf-config.js"

    def _check_md_to_pdf_installed(self) -> None:
        """
        Check if md-to-pdf is available in the system.

        Raises:
            MdToPdfNotFoundError: If md-to-pdf is not installed.
        """
        if shutil.which("md-to-pdf") is None:
            raise MdToPdfNotFoundError(
                "md-to-pdf command not found. Please install it with:\n"
                "  npm install -g md-to-pdf\n"
                "or\n"
                "  pnpm add -g md-to-pdf"
            )

    def convert(self, input_path: Path, output_path: Path) -> None:
        """
        Convert a Markdown file to PDF.

        Args:
            input_path: Path to the source Markdown file.
            output_path: Path where the PDF file will be written.

        Raises:
            FileNotFoundError: If input file does not exist.
            MdToPdfNotFoundError: If md-to-pdf is not installed.
            ConversionError: If conversion fails.
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        if not self.supports_extension(input_path.suffix):
            raise ConversionError(
                f"Unsupported file extension: {input_path.suffix}. "
                f"Supported: {self.SUPPORTED_EXTENSIONS}"
            )

        self._check_md_to_pdf_installed()

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Build command
        cmd = [
            "md-to-pdf",
            str(input_path),
            "--config-file",
            str(self._config_path),
        ]

        try:
            # md-to-pdf outputs to the same directory as input by default
            # We need to move it to the output path after conversion
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                cwd=str(input_path.parent),
            )

            # md-to-pdf creates the PDF in the same directory as the input file
            generated_pdf = input_path.with_suffix(".pdf")

            if generated_pdf.exists() and generated_pdf != output_path:
                shutil.move(str(generated_pdf), str(output_path))
            elif not output_path.exists():
                raise ConversionError(
                    f"PDF was not generated. Command output: {result.stdout}"
                )

        except subprocess.CalledProcessError as e:
            raise ConversionError(
                f"Failed to convert {input_path}: {e.stderr or e.stdout}"
            ) from e

    def supports_extension(self, extension: str) -> bool:
        """
        Check if this converter supports the given file extension.

        Args:
            extension: File extension (e.g., '.md').

        Returns:
            True if the extension is supported.
        """
        return extension.lower() in self.SUPPORTED_EXTENSIONS


_: ConverterProtocol = MdHandler()
