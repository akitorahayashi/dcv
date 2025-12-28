# dcv

`dcv` (Document Converter CLI) is a pure Python command-line tool for converting documents between PDF and Markdown formats. Built with Typer, featuring dependency injection for extensibility and testability.

## Features

- **PDF to Markdown**: Convert PDF files to Markdown using [markitdown](https://github.com/microsoft/markitdown)
- **Markdown to PDF**: Convert Markdown files to styled PDFs using [Playwright](https://playwright.dev/) with MathJax support
- **Batch Processing**: Convert entire directories of files at once
- **Customizable Output**: Specify output directories for converted files
- **MathJax Support**: Full LaTeX equation rendering in PDF output
- **Pure Python**: No Node.js dependencies required

## 🚀 Installation

### Install with pipx (Recommended)

Install directly from GitHub using [pipx](https://pipx.pypa.io/):

```shell
pipx install git+https://github.com/akitorahayashi/dcv.git
```

After installation, install Playwright browsers (required for PDF generation):

```shell
playwright install chromium
```

The `dcv` command is now available globally:

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

Then install Playwright browsers:

```shell
uv run playwright install chromium
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
| `--css` | `-c` | Custom CSS file for PDF styling (md2pdf only) |
| `--margin-top` | | Top margin override (md2pdf only, e.g., "35mm") |
| `--margin-bottom` | | Bottom margin override (md2pdf only) |
| `--margin-left` | | Left margin override (md2pdf only) |
| `--margin-right` | | Right margin override (md2pdf only) |

## 🎨 Customizing PDF Output

### Export Default Assets

Export dcv's default CSS and HTML template for customization:

```shell
dcv scaffold --css              # Export CSS stylesheet
dcv scaffold --template         # Export HTML template
dcv scaffold --all              # Export both
dcv scaffold --all -o custom/   # Export to custom/ directory
```

### Using Custom Styles

Create a custom stylesheet:

```shell
dcv scaffold --css
# Creates dcv_custom.css in current directory
```

Edit `dcv_custom.css` to match your requirements:

```css
@page {
  size: A4;
  margin-top: 35mm;    /* Academic paper margins */
  margin-bottom: 30mm;
  margin-left: 30mm;
  margin-right: 30mm;
}

body {
  font-family: "Times New Roman", serif;
  font-size: 12pt;
  text-align: justify;
  line-height: 2.0;
}

h1 {
  font-size: 16pt;
  text-align: center;
}
```

Use your custom stylesheet:

```shell
dcv md2pdf -f paper.md --css dcv_custom.css
```

### Quick Margin Overrides

For one-off changes without creating a CSS file:

```shell
dcv md2pdf -f doc.md --margin-top 35mm --margin-bottom 25mm
```

### Configuration Precedence

Settings are applied in this order (highest to lowest priority):

1. **CLI `--margin-*` flags** - Override everything
2. **Custom CSS via `--css` flag** - Override default styles
3. **Default bundled CSS** - Base styling

### Examples

**Academic Thesis (Japanese University)**
```shell
# Create custom CSS
dcv scaffold --css

# Edit dcv_custom.css for thesis requirements
cat > dcv_custom.css <<EOF
@page {
  size: A4;
  margin-top: 35mm;
  margin-bottom: 30mm;
  margin-left: 30mm;
  margin-right: 30mm;
}

body {
  font-family: "Noto Serif JP", serif;
  font-size: 10.5pt;
  text-align: justify;
  line-height: 2.0;
}
EOF

# Convert thesis
dcv md2pdf -f thesis.md --css dcv_custom.css
```

**Business Report**
```shell
dcv md2pdf -f report.md --margin-top 25mm --margin-bottom 25mm
```

**Two-Column Academic Paper**
```css
/* In dcv_custom.css */
.markdown-body {
  column-count: 2;
  column-gap: 10mm;
}

h1, h2 {
  column-span: all;  /* Full-width headings */
}
```

### Options

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
│       ├── container.py     # DI container and context
│       ├── assets/          # Static resources
│       │   ├── templates/   # HTML templates for PDF generation
│       │   │   └── base.html
│       │   └── styles/      # CSS stylesheets for PDF styling
│       │       └── pdf.css
│       ├── commands/
│       │   ├── pdf2md.py     # pdf2md command
│       │   ├── md2pdf.py     # md2pdf command
│       │   ├── scaffold.py   # scaffold command
│       │   └── validate_options.py # Shared command utilities
│       ├── config/
│       │   └── settings.py  # Pydantic settings
│       ├── protocols/       # Protocol definitions for service interfaces
│       └── services/        # Converter implementations
│           ├── pdf_converter.py   # PDF to Markdown conversion
│           ├── md_converter.py    # Markdown to PDF conversion (Playwright)
│           └── file_manager.py  # File discovery and path resolution
├── tests/
│   ├── fixtures/            # Test fixtures (sample.md, sample_with_math.md)
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
dcv scaffold --help     # Export default assets for customization
```

## 📋 Dependencies

- **Python 3.10+**
- **[markitdown](https://github.com/microsoft/markitdown)** - PDF to Markdown conversion
- **[Playwright](https://playwright.dev/)** - Browser automation for PDF generation
- **[markdown-it-py](https://github.com/executablebooks/markdown-it-py)** - Markdown parsing
- **[Jinja2](https://jinja.palletsprojects.com/)** - HTML template engine
- **[Typer](https://typer.tiangolo.com/)** - CLI framework
- **[Rich](https://rich.readthedocs.io/)** - Terminal formatting
- **[Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)** - Configuration management
