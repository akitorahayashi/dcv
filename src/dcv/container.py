"""Dependency injection container for the dcv CLI application."""

from dataclasses import dataclass
from pathlib import Path

from dcv.config.settings import AppSettings
from dcv.protocols.converter_protocol import ConverterProtocol
from dcv.services import MdConverter, PdfConverter
from dcv.services.file_manager import FileManager


@dataclass
class AppContext:
    """Application context holding settings and service instances."""

    settings: AppSettings
    pdf_converter: ConverterProtocol
    md_converter: ConverterProtocol
    file_manager: FileManager


def create_container(
    settings: AppSettings | None = None,
    pdf_converter: ConverterProtocol | None = None,
    md_converter: ConverterProtocol | None = None,
    file_manager: FileManager | None = None,
) -> AppContext:
    """
    Create and return the application context with all dependencies wired.

    Args:
        settings: Optional pre-configured settings. If None, loads from environment.
        pdf_converter: Optional PDF converter override for testing.
        md_converter: Optional MD converter override for testing.
        file_manager: Optional file manager override for testing.

    Returns:
        AppContext with settings and services initialized.
    """
    if settings is None:
        settings = AppSettings()

    if pdf_converter is None:
        pdf_converter = PdfConverter()

    if md_converter is None:
        md_converter = MdConverter()

    if file_manager is None:
        file_manager = FileManager(output_dir=Path(settings.default_output_dir))

    return AppContext(
        settings=settings,
        pdf_converter=pdf_converter,
        md_converter=md_converter,
        file_manager=file_manager,
    )
