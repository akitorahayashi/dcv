Sample Document

This file is a sample Markdown for the PDF and Markdown conversion tool "dcv".

Table of Contents

1. Overview

2. Features

3. Usage

4. Command Examples

5. Reference Links

Overview

dcv is a CLI tool that allows easy conversion between PDF and Markdown. It is designed based on Typer, with dependency injection and extensibility through protocols.

Features

PDF→Markdown conversion uses markitdown
Markdown→PDF conversion uses Playwright (Python package)
High-quality PDF rendering with Chromium

Simple CLI command design

Highly extensible service provider configuration

Usage

Convert PDF to Markdown

dcv pdf2md input.pdf output.md

Convert Markdown to PDF

dcv md2pdf input.md output.pdf

Command Examples

# PDF→Markdown

dcv pdf2md ./docs/sample.pdf ./docs/sample.md

# Markdown→PDF

dcv md2pdf ./docs/sample.md ./docs/sample.pdf

Reference Links

markitdown

Playwright

Typer

This sample is used for verifying dcv operation and creating images of conversion results.

