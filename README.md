# dcv

`dcv` (Document Converter CLI) is a command-line tool for converting documents between PDF and Markdown formats. Built on top of Typer with dependency injection for extensibility and testability.

## Features

- **PDF to Markdown**: Convert PDF files to Markdown using [markitdown](https://github.com/microsoft/markitdown)
- **Markdown to PDF**: Convert Markdown files to PDF using [md-to-pdf](https://github.com/simonhaenisch/md-to-pdf)
- **Batch Processing**: Convert entire directories of files at once
- **Customizable Output**: Specify output directories for converted files

## 🚀 Installation

### Install with pipx (Recommended)

Install directly from GitHub using [pipx](https://pipx.pypa.io/):

```shell
pipx install git+https://github.com/akitorahayashi/dcv.git
```

After installation, the `dcv` command is available globally:

```shell
dcv --version
dcv --help
```

### Development Setup

For development, clone the repository and use [uv](https://github.com/astral-sh/uv):

```shell
git clone https://github.com/akitorahayashi/dcv.git
cd dcv
just setup
```

This installs dependencies with `uv` and creates a local `.env` file if one does not exist.

### Prerequisites for md2pdf

The `md2pdf` command requires [md-to-pdf](https://github.com/simonhaenisch/md-to-pdf) to be installed:

```shell
npm install -g md-to-pdf
# or
pnpm add -g md-to-pdf
```

## 📖 Usage

### Convert PDF to Markdown

```shell
# Single file
dcv pdf2md -f document.pdf

# Directory (recursive)
dcv pdf2md -d ./pdfs -o ./markdown_output
```

### Convert Markdown to PDF

```shell
# Single file
dcv md2pdf -f document.md

# Directory (recursive)
dcv md2pdf -d ./markdown -o ./pdf_output
```

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--file` | `-f` | Input file to convert |
| `--dir` | `-d` | Input directory containing files to convert |
| `--output-dir` | `-o` | Output directory (default: `dcv_output`) |

### Run during Development

```shell
just run --help
just run pdf2md -f document.pdf
just run md2pdf -f document.md
just run --version
```

Or directly via Python:

```shell
uv run python -m dcv --help
uv run python -m dcv pdf2md -f document.pdf
```

### Run Tests and Linters

```shell
just test       # run all tests (unit + intg)
just unit-test  # run unit tests only
just intg-test  # run integration tests only
just check      # ruff format --check, ruff check, and mypy
just fix        # auto-format with ruff format and ruff --fix
```

## 🧱 Project Structure

```
├── src/
│   └── dcv/
│       ├── __init__.py
│       ├── __main__.py      # python -m dcv entry point
│       ├── main.py          # Typer app factory and command registration
│       ├── assets/          # Static resources
│       │   └── md-to-pdf-config.js  # Default PDF styling configuration
│       ├── commands/
│       │   └── converter.py # pdf2md and md2pdf commands
│       ├── config/
│       │   └── settings.py  # Pydantic settings
│       ├── core/
│       │   └── container.py # DI container and context
│       ├── protocols/       # Protocol definitions for service interfaces
│       └── services/        # Converter implementations
│           ├── pdf_handler.py   # PDF to Markdown conversion
│           ├── md_handler.py    # Markdown to PDF conversion
│           └── file_manager.py  # File discovery and path resolution
├── tests/
│   ├── unit/                # Pure unit tests (service layer)
│   └── intg/                # Integration tests (CLI with CliRunner)
├── justfile
└── pyproject.toml
```

## 🔧 Configuration

Environment variables can be set in `.env`:

- `DCV_APP_NAME` – application display name (default `dcv`)
- `DCV_OUTPUT_DIR` – default output directory (default `dcv_output`)

## ✅ Commands

```shell
dcv --version           # Show version
dcv --help              # Show help
dcv pdf2md --help       # PDF to Markdown conversion help
dcv md2pdf --help       # Markdown to PDF conversion help
```

## 📋 Dependencies

- **Python 3.10+**
- **[markitdown](https://github.com/microsoft/markitdown)** - PDF to Markdown conversion
- **[md-to-pdf](https://github.com/simonhaenisch/md-to-pdf)** (npm) - Markdown to PDF conversion
- **[Typer](https://typer.tiangolo.com/)** - CLI framework
- **[Rich](https://rich.readthedocs.io/)** - Terminal formatting
- **[Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)** - Configuration management
