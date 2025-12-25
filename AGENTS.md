# dcv Agent Notes

## Overview
- Document Converter CLI for converting between PDF and Markdown formats.
- Built on Typer with dependency injection using context objects, protocols for interfaces, and factory pattern for services.

## Design Philosophy
- Use `markitdown` for PDF to Markdown conversion.
- Use `md-to-pdf` (npm package) for Markdown to PDF conversion.
- Keep the CLI simple with two main commands: `pdf2md` and `md2pdf`.
- Use Typer-native `ctx.obj` pattern with protocols for service interfaces.
- Maintain parity between local and CI flows with a single source of truth (`just`, `uv`, `.env`).

## Key Files
- `src/dcv/core/container.py`: Central place to wire settings and service providers.
- `src/dcv/main.py`: Typer app instantiation; commands registered at root level.
- `src/dcv/commands/converter.py`: pdf2md and md2pdf command implementations.
- `src/dcv/protocols/converter_protocol.py`: Protocol definition for converter services.
- `src/dcv/services/pdf_handler.py`: PDF to Markdown conversion using markitdown.
- `src/dcv/services/md_handler.py`: Markdown to PDF conversion using md-to-pdf subprocess.
- `src/dcv/services/file_manager.py`: File discovery, path resolution, and batch processing.
- `src/dcv/assets/md-to-pdf-config.js`: Default PDF styling configuration.
- `tests/`: Unit and integration tests.

## Tooling Snapshot
- `justfile`: run/lint/test tasks (`unit-test`, `intg-test`) used locally and in CI. Prefer `just test` as the unified entrypoint.
- `uv.lock` + `pyproject.toml`: Reproducible dependency graph; regenerate with `uv pip compile` when deps change.

## External Dependencies
- `md-to-pdf` must be installed via npm/pnpm: `npm install -g md-to-pdf`
- Requires Google Chrome for PDF rendering (configured in `md-to-pdf-config.js`)
