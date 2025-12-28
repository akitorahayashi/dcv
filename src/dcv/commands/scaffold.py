"""Scaffold command for exporting default assets."""

from importlib import resources
from pathlib import Path

import typer
from rich.console import Console

app = typer.Typer()
console = Console()


@app.command("scaffold")
def scaffold(
    output_dir: Path = typer.Option(
        Path.cwd(),
        "--output-dir",
        "-o",
        help="Directory to write scaffolded files.",
        resolve_path=True,
    ),
    css: bool = typer.Option(
        False,
        "--css",
        help="Export default CSS stylesheet.",
    ),
    template: bool = typer.Option(
        False,
        "--template",
        help="Export default HTML template.",
    ),
    all: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Export all assets (CSS + template).",
    ),
) -> None:
    """
    Export default assets for customization.

    Use this command to create local copies of dcv's bundled assets
    (CSS stylesheets and HTML templates) that you can customize.

    Examples:
        dcv scaffold --css              # Export pdf.css to current dir
        dcv scaffold --template         # Export HTML template
        dcv scaffold --all              # Export all assets
        dcv scaffold --all -o custom/   # Export to custom/ directory
    """
    if not (css or template or all):
        console.print(
            "[yellow]No assets specified.[/yellow] "
            "Use --css, --template, or --all to export assets."
        )
        raise typer.Exit(0)

    exported = []

    if css or all:
        try:
            css_content = _load_bundled_asset("dcv.assets.styles", "pdf.css")
            css_path = output_dir / "dcv_custom.css"
            css_path.parent.mkdir(parents=True, exist_ok=True)
            css_path.write_text(css_content, encoding="utf-8")
            exported.append(str(css_path))
        except Exception as e:
            console.print(f"[red]Error exporting CSS:[/red] {e}")
            raise typer.Exit(1)

    if template or all:
        try:
            template_content = _load_bundled_asset(
                "dcv.assets.templates", "base.html.jinja"
            )
            template_path = output_dir / "dcv_custom_template.html"
            template_path.parent.mkdir(parents=True, exist_ok=True)
            template_path.write_text(template_content, encoding="utf-8")
            exported.append(str(template_path))
        except Exception as e:
            console.print(f"[red]Error exporting template:[/red] {e}")
            raise typer.Exit(1)

    console.print("[green]✓[/green] Exported assets:")
    for path in exported:
        console.print(f"  • [cyan]{path}[/cyan]")

    console.print("\n[dim]Edit these files to customize your PDF output.[/dim]")


def _load_bundled_asset(package: str, filename: str) -> str:
    """
    Load bundled asset content from package resources.

    Args:
        package: Package path (e.g., "dcv.assets.styles").
        filename: Asset filename (e.g., "pdf.css").

    Returns:
        Asset file content as string.

    Raises:
        FileNotFoundError: If asset cannot be loaded.
    """
    try:
        with resources.as_file(
            resources.files(package).joinpath(filename)
        ) as asset_file:
            return Path(asset_file).read_text(encoding="utf-8")
    except (TypeError, FileNotFoundError):
        # Fallback for development environment
        asset_path_parts = package.split(".")[
            1:
        ]  # e.g., ['assets', 'styles'] from 'dcv.assets.styles'
        fallback_path = Path(__file__).parent.parent.joinpath(
            *asset_path_parts, filename
        )
        return fallback_path.read_text(encoding="utf-8")
