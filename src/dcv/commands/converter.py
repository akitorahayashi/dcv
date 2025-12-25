"""Document conversion commands for dcv CLI."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from dcv.core.container import AppContext

converter_app = typer.Typer(help="Document conversion commands.")
console = Console()


def _validate_input_options(
    file: Optional[Path], directory: Optional[Path]
) -> tuple[Path, bool]:
    """
    Validate and return the input source.

    Args:
        file: Optional file path.
        directory: Optional directory path.

    Returns:
        Tuple of (source_path, is_directory).

    Raises:
        typer.BadParameter: If neither or both options are provided.
    """
    if file is None and directory is None:
        raise typer.BadParameter(
            "Either --file/-f or --dir/-d must be specified."
        )

    if file is not None and directory is not None:
        raise typer.BadParameter(
            "Cannot specify both --file/-f and --dir/-d. Choose one."
        )

    if file is not None:
        return file, False
    return directory, True  # type: ignore


@converter_app.command("pdf2md")
def pdf2md(
    ctx: typer.Context,
    file: Optional[Path] = typer.Option(
        None,
        "--file",
        "-f",
        help="Input PDF file to convert.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
    directory: Optional[Path] = typer.Option(
        None,
        "--dir",
        "-d",
        help="Input directory containing PDF files.",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    output_dir: Path = typer.Option(
        Path("dcv_output"),
        "--output-dir",
        "-o",
        help="Output directory for converted Markdown files.",
        resolve_path=True,
    ),
) -> None:
    """
    Convert PDF file(s) to Markdown.

    Examples:
        dcv pdf2md -f document.pdf
        dcv pdf2md -d ./pdfs -o ./markdown_output
    """
    app_ctx: AppContext = ctx.obj

    try:
        source, is_dir = _validate_input_options(file, directory)
    except typer.BadParameter as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    # Update file manager output directory
    app_ctx.file_manager._output_dir = output_dir
    app_ctx.file_manager.ensure_output_dir()

    # Generate path pairs and convert
    input_extensions = {".pdf"}
    output_extension = ".md"
    converted_count = 0
    error_count = 0

    source_dir = source if is_dir else None

    for input_path, output_path in app_ctx.file_manager.generate_path_pairs(
        source, input_extensions, output_extension
    ):
        try:
            console.print(f"Converting: [cyan]{input_path.name}[/cyan]...")
            app_ctx.pdf_handler.convert(input_path, output_path)
            console.print(f"  → [green]{output_path}[/green]")
            converted_count += 1
        except Exception as e:
            console.print(f"  [red]Error:[/red] {e}")
            error_count += 1

    # Summary
    console.print()
    if converted_count > 0:
        console.print(f"[green]✓ Converted {converted_count} file(s)[/green]")
    if error_count > 0:
        console.print(f"[red]✗ Failed {error_count} file(s)[/red]")
    if converted_count == 0 and error_count == 0:
        console.print("[yellow]No PDF files found to convert.[/yellow]")


@converter_app.command("md2pdf")
def md2pdf(
    ctx: typer.Context,
    file: Optional[Path] = typer.Option(
        None,
        "--file",
        "-f",
        help="Input Markdown file to convert.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
    directory: Optional[Path] = typer.Option(
        None,
        "--dir",
        "-d",
        help="Input directory containing Markdown files.",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    output_dir: Path = typer.Option(
        Path("dcv_output"),
        "--output-dir",
        "-o",
        help="Output directory for converted PDF files.",
        resolve_path=True,
    ),
) -> None:
    """
    Convert Markdown file(s) to PDF.

    Requires md-to-pdf to be installed: npm install -g md-to-pdf

    Examples:
        dcv md2pdf -f document.md
        dcv md2pdf -d ./markdown -o ./pdf_output
    """
    app_ctx: AppContext = ctx.obj

    try:
        source, is_dir = _validate_input_options(file, directory)
    except typer.BadParameter as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    # Update file manager output directory
    app_ctx.file_manager._output_dir = output_dir
    app_ctx.file_manager.ensure_output_dir()

    # Generate path pairs and convert
    input_extensions = {".md", ".markdown"}
    output_extension = ".pdf"
    converted_count = 0
    error_count = 0

    for input_path, output_path in app_ctx.file_manager.generate_path_pairs(
        source, input_extensions, output_extension
    ):
        try:
            console.print(f"Converting: [cyan]{input_path.name}[/cyan]...")
            app_ctx.md_handler.convert(input_path, output_path)
            console.print(f"  → [green]{output_path}[/green]")
            converted_count += 1
        except Exception as e:
            console.print(f"  [red]Error:[/red] {e}")
            error_count += 1

    # Summary
    console.print()
    if converted_count > 0:
        console.print(f"[green]✓ Converted {converted_count} file(s)[/green]")
    if error_count > 0:
        console.print(f"[red]✗ Failed {error_count} file(s)[/red]")
    if converted_count == 0 and error_count == 0:
        console.print("[yellow]No Markdown files found to convert.[/yellow]")
