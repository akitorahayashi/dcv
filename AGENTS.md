# dcv Agent Notes

## Overview
- Document Converter CLI for converting between PDF and Markdown formats.
- Built on Typer with dependency injection using context objects, protocols for interfaces, and factory pattern for services.

## Design Philosophy
- Use `markitdown` for PDF to Markdown conversion.
- Use `Playwright` (Python) with `markdown-it-py` and `Jinja2` for Markdown to PDF conversion.
- **CSS-first layout**: Use CSS `@page` rules for page layout, not Python constants. This allows users to customize PDF output without modifying code.
- **User customization**: Provide `scaffold` command to export editable default assets (CSS, templates).
- **Configuration hierarchy**: CLI flags > custom CSS > bundled CSS. This gives users control at multiple levels.
- Keep the CLI simple with commands: `pdf2md`, `md2pdf`, and `scaffold`.
- Use Typer-native `ctx.obj` pattern with protocols for service interfaces.
- Maintain parity between local and CI flows with a single source of truth (`just`, `uv`, `.env`).
- Separate concerns: HTML templates, CSS stylesheets, and Python logic.

## Key Files
- `src/dcv/container.py`: Central place to wire settings and service providers.
- `src/dcv/main.py`: Typer app instantiation; commands registered at root level.
- `src/dcv/commands/pdf2md.py`: pdf2md command implementation.
- `src/dcv/commands/md2pdf.py`: md2pdf command implementation with CSS and margin options.
- `src/dcv/commands/scaffold.py`: scaffold command for exporting default assets.
- `src/dcv/commands/validate_options.py`: Shared command utilities.
- `src/dcv/protocols/converter_protocol.py`: Protocol definition for converter services (accepts `**kwargs`).
- `src/dcv/services/pdf_converter.py`: PDF to Markdown conversion using markitdown.
- `src/dcv/services/md_converter.py`: Markdown to PDF conversion using Playwright with CSS-first layout and async support. Handles custom CSS injection and margin overrides.
- `src/dcv/services/file_manager.py`: File discovery, path resolution, and batch processing.
- `src/dcv/assets/templates/base.html`: HTML template with MathJax configuration.
- `src/dcv/assets/styles/pdf.css`: CSS stylesheet with `@page` rules for PDF layout (A4, 30mm/20mm margins).
- `tests/fixtures/`: Sample files for testing (sample.md, sample_with_math.md, custom_style.css, academic_style.css).
- `tests/unit/`: Unit tests with mocks and async test support. Includes tests for margin validation and CSS loading.
- `tests/intg/`: Integration tests organized by purpose (test_cli_commands.py, test_container.py, test_pdf2md_conversion.py, test_md2pdf_conversion.py, test_scaffold_command.py).

## Tooling Snapshot
- `justfile`: run/lint/test tasks (`unit-test`, `intg-test`) used locally and in CI. Prefer `just test` as the unified entrypoint.
- `uv.lock` + `pyproject.toml`: Reproducible dependency graph; regenerate with `uv pip compile` when deps change.

## External Dependencies
- `playwright` must be installed and browsers set up: `playwright install chromium`
- No Node.js dependencies required (pure Python solution)
- CSS-aware PDF generation: Playwright's `prefer_css_page_size` is enabled to honor CSS `@page` rules

