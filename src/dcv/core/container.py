"""Dependency injection container for the dcv CLI application."""

from dataclasses import dataclass
from pathlib import Path

from dcv.config.settings import AppSettings
from dcv.protocols.converter_protocol import ConverterProtocol
from dcv.services.file_manager import FileManager
from dcv.services.md_handler import MdHandler
from dcv.services.pdf_handler import PdfHandler


@dataclass
class AppContext:
    """Application context holding settings and service instances."""

    settings: AppSettings
    pdf_handler: ConverterProtocol
    md_handler: ConverterProtocol
    file_manager: FileManager


def create_container(
    settings: AppSettings | None = None,
    pdf_handler: ConverterProtocol | None = None,
    md_handler: ConverterProtocol | None = None,
    file_manager: FileManager | None = None,
) -> AppContext:
    """
    Create and return the application context with all dependencies wired.

    Args:
        settings: Optional pre-configured settings. If None, loads from environment.
        pdf_handler: Optional PDF handler override for testing.
        md_handler: Optional MD handler override for testing.
        file_manager: Optional file manager override for testing.

    Returns:
        AppContext with settings and services initialized.
    """
    if settings is None:
        settings = AppSettings()

    if pdf_handler is None:
        pdf_handler = PdfHandler()

    if md_handler is None:
        md_handler = MdHandler()

    if file_manager is None:
        file_manager = FileManager(output_dir=Path(settings.default_output_dir))

    return AppContext(
        settings=settings,
        pdf_handler=pdf_handler,
        md_handler=md_handler,
        file_manager=file_manager,
    )
