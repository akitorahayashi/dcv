# dcv Agent Notes

## Overview
- Document Converter CLI for converting between PDF and Markdown formats.
- Built on Typer with dependency injection using context objects, protocols for interfaces, and factory pattern for services.

## Design Philosophy
- Use `markitdown` for PDF to Markdown conversion.
- Use `Playwright` (Python) with `markdown-it-py` and `Jinja2` for Markdown to PDF conversion.
- Keep the CLI simple with two main commands: `pdf2md` and `md2pdf`.
- Use Typer-native `ctx.obj` pattern with protocols for service interfaces.
- Maintain parity between local and CI flows with a single source of truth (`just`, `uv`, `.env`).
- Separate concerns: HTML templates, CSS stylesheets, and Python logic.

## Key Files
- `src/dcv/container.py`: Central place to wire settings and service providers.
- `src/dcv/main.py`: Typer app instantiation; commands registered at root level.
- `src/dcv/commands/pdf2md.py`: pdf2md command implementation.
- `src/dcv/commands/md2pdf.py`: md2pdf command implementation.
- `src/dcv/commands/validate_options.py`: Shared command utilities.
- `src/dcv/protocols/converter_protocol.py`: Protocol definition for converter services.
- `src/dcv/services/pdf_converter.py`: PDF to Markdown conversion using markitdown.
- `src/dcv/services/md_converter.py`: Markdown to PDF conversion using Playwright with async support.
- `src/dcv/services/file_manager.py`: File discovery, path resolution, and batch processing.
- `src/dcv/assets/templates/base.html`: HTML template with MathJax configuration.
- `src/dcv/assets/styles/pdf.css`: CSS stylesheet for PDF styling.
- `tests/fixtures/`: Sample files for testing (sample.md, sample_with_math.md).
- `tests/unit/`: Unit tests with mocks and async test support.
- `tests/intg/`: Integration tests organized by purpose (test_cli_commands.py, test_container.py, test_pdf2md_conversion.py, test_md2pdf_conversion.py).

## Tooling Snapshot
- `justfile`: run/lint/test tasks (`unit-test`, `intg-test`) used locally and in CI. Prefer `just test` as the unified entrypoint.
- `uv.lock` + `pyproject.toml`: Reproducible dependency graph; regenerate with `uv pip compile` when deps change.

## External Dependencies
- `playwright` must be installed and browsers set up: `playwright install chromium`
- No Node.js dependencies required (pure Python solution)

