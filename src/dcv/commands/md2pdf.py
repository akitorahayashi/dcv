"""Markdown to PDF conversion command."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from dcv.commands.validate_options import validate_input_options
from dcv.container import AppContext

app = typer.Typer()
console = Console()


@app.command("md2pdf")
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
    css: Optional[Path] = typer.Option(
        None,
        "--css",
        "-c",
        help="Custom CSS file for PDF styling.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
    margin_top: Optional[str] = typer.Option(
        None,
        "--margin-top",
        help="Top margin (e.g., '35mm', '1in'). Overrides CSS.",
    ),
    margin_right: Optional[str] = typer.Option(
        None,
        "--margin-right",
        help="Right margin (e.g., '20mm'). Overrides CSS.",
    ),
    margin_bottom: Optional[str] = typer.Option(
        None,
        "--margin-bottom",
        help="Bottom margin (e.g., '30mm'). Overrides CSS.",
    ),
    margin_left: Optional[str] = typer.Option(
        None,
        "--margin-left",
        help="Left margin (e.g., '25mm'). Overrides CSS.",
    ),
) -> None:
    """
    Convert Markdown file(s) to PDF.

    Requires Playwright browsers: playwright install chromium

    Examples:
        dcv md2pdf -f document.md
        dcv md2pdf -f document.md --css custom.css
        dcv md2pdf -f document.md --margin-top 35mm --margin-bottom 30mm
        dcv md2pdf -d ./markdown -o ./pdf_output
    """
    app_ctx: AppContext = ctx.obj

    try:
        source, is_dir = validate_input_options(file, directory)
    except typer.BadParameter as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    app_ctx.file_manager.output_dir = output_dir
    app_ctx.file_manager.ensure_output_dir()

    input_extensions = {".md", ".markdown"}
    output_extension = ".pdf"
    converted_count = 0
    error_count = 0

    for input_path, output_path in app_ctx.file_manager.generate_path_pairs(
        source, input_extensions, output_extension
    ):
        try:
            console.print(f"Converting: [cyan]{input_path.name}[/cyan]...")
            app_ctx.md_converter.convert(
                input_path,
                output_path,
                css_path=css,
                margin_top=margin_top,
                margin_right=margin_right,
                margin_bottom=margin_bottom,
                margin_left=margin_left,
            )
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
        console.print("[yellow]No Markdown files found to convert.[/yellow]")
