"""PDF to Markdown conversion command."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from dcv.commands.validate_options import validate_input_options
from dcv.container import AppContext

app = typer.Typer()
console = Console()


@app.command("pdf2md")
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
        source, is_dir = validate_input_options(file, directory)
    except typer.BadParameter as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    app_ctx.file_manager.output_dir = output_dir
    app_ctx.file_manager.ensure_output_dir()

    input_extensions = {".pdf"}
    output_extension = ".md"
    converted_count = 0
    error_count = 0

    for input_path, output_path in app_ctx.file_manager.generate_path_pairs(
        source, input_extensions, output_extension
    ):
        try:
            console.print(f"Converting: [cyan]{input_path.name}[/cyan]...")
            app_ctx.pdf_converter.convert(input_path, output_path)
            console.print(f"  → [green]{output_path}[/green]")
            converted_count += 1
        except Exception as e:
            console.print(f"  [red]Error:[/red] {e}")
            error_count += 1

    console.print()
    if converted_count > 0:
        console.print(f"[green]✓ Converted {converted_count} file(s)[/green]")
    if error_count > 0:
        console.print(f"[red]✗ Failed {error_count} file(s)[/red]")
        raise typer.Exit(1)
    if converted_count == 0 and error_count == 0:
        console.print("[yellow]No PDF files found to convert.[/yellow]")
