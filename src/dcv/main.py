"""Typer CLI application entry point for dcv."""

from importlib import metadata
from typing import Optional

import typer
from rich.console import Console

from dcv.commands import md2pdf_app, pdf2md_app, scaffold_app
from dcv.container import create_container

console = Console()


def get_safe_version(package_name: str, fallback: str = "0.1.0") -> str:
    """
    Safely get the version of a package.

    Args:
        package_name: Name of the package
        fallback: Default version if retrieval fails

    Returns:
        Version string
    """
    try:
        return metadata.version(package_name)
    except metadata.PackageNotFoundError:
        return fallback


def version_callback(value: bool | None) -> None:
    """Print version and exit."""
    if value:
        version = get_safe_version("dcv")
        console.print(f"dcv version: {version}")
        raise typer.Exit()


app = typer.Typer(
    name="dcv",
    help="Document Converter CLI - Convert between PDF and Markdown formats.",
    no_args_is_help=True,
)

# Register commands at root level
app.add_typer(pdf2md_app, name="")
app.add_typer(md2pdf_app, name="")
app.add_typer(scaffold_app, name="")


@app.callback()
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """
    dcv - Document Converter CLI.

    Convert PDF files to Markdown or Markdown files to PDF.
    """
    # Initialize the application context
    ctx.obj = create_container()


if __name__ == "__main__":
    app()
