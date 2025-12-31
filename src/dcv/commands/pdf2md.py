"""PDF to Markdown conversion command."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from dcv.container import AppContext

app = typer.Typer()
console = Console()


@app.command("pdf2md")
def pdf2md(
    ctx: typer.Context,
    path: Path = typer.Argument(
        ...,
        help="Input PDF file or directory containing PDF files.",
        exists=True,
        file_okay=True,
        dir_okay=True,
        resolve_path=True,
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Output directory for converted files. Default: same dir for file, ./dcv_outputs for dir.",
        resolve_path=True,
    ),
) -> None:
    """
    Convert PDF file(s) to Markdown.

    Examples:
        dcv pdf2md document.pdf
        dcv pdf2md ./pdfs
        dcv pdf2md ./pdfs -o ./custom_output
    """
    app_ctx: AppContext = ctx.obj
    is_dir = path.is_dir()

    # Determine output directory
    if output_dir is not None:
        resolved_output_dir = output_dir
    elif is_dir:
        resolved_output_dir = Path("dcv_outputs")
    else:
        resolved_output_dir = path.parent

    app_ctx.file_manager.output_dir = resolved_output_dir
    if is_dir or output_dir is not None:
        app_ctx.file_manager.ensure_output_dir()

    input_extensions = {".pdf"}
    output_extension = ".md"
    converted_count = 0
    error_count = 0

    for input_path, output_path in app_ctx.file_manager.generate_path_pairs(
        path, input_extensions, output_extension
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
