"""Unit tests for the Markdown to PDF handler service."""

import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from dcv.errors import ConversionError
from dcv.services import MdConverter, MdToPdfNotFoundError

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


class TestMdConverter:
    """Unit tests for MdConverter."""

    def test_supports_extension_md(self):
        """Test that .md extension is supported."""
        handler = MdConverter()
        assert handler.supports_extension(".md") is True
        assert handler.supports_extension(".MD") is True
        assert handler.supports_extension(".markdown") is True

    def test_supports_extension_unsupported(self):
        """Test that unsupported extensions return False."""
        handler = MdConverter()
        assert handler.supports_extension(".pdf") is False
        assert handler.supports_extension(".txt") is False
        assert handler.supports_extension(".docx") is False

    def test_convert_file_not_found(self, tmp_path: Path):
        """Test that FileNotFoundError is raised for missing input."""
        handler = MdConverter()
        input_path = tmp_path / "nonexistent.md"
        output_path = tmp_path / "output.pdf"

        with pytest.raises(FileNotFoundError, match="Input file not found"):
            handler.convert(input_path, output_path)

    def test_convert_unsupported_extension(self, tmp_path: Path):
        """Test that ConversionError is raised for unsupported file types."""
        handler = MdConverter()
        input_path = tmp_path / "document.txt"
        input_path.write_text("test content")
        output_path = tmp_path / "output.pdf"

        with pytest.raises(ConversionError, match="Unsupported file extension"):
            handler.convert(input_path, output_path)

    @patch("shutil.which")
    def test_convert_md_to_pdf_not_installed(
        self, mock_which: MagicMock, tmp_path: Path
    ):
        """Test that MdToPdfNotFoundError is raised when md-to-pdf is not installed."""
        mock_which.return_value = None
        handler = MdConverter()

        input_path = tmp_path / "document.md"
        input_path.write_text("# Test Document")
        output_path = tmp_path / "output.pdf"

        with pytest.raises(MdToPdfNotFoundError, match="md-to-pdf command not found"):
            handler.convert(input_path, output_path)

    @patch("subprocess.run")
    @patch("shutil.which")
    @patch("shutil.move")
    def test_convert_success(
        self,
        mock_move: MagicMock,
        mock_which: MagicMock,
        mock_run: MagicMock,
        tmp_path: Path,
    ):
        """Test successful Markdown to PDF conversion."""
        mock_which.return_value = "/usr/local/bin/md-to-pdf"
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        handler = MdConverter(config_path=tmp_path / "config.js")

        input_path = tmp_path / "document.md"
        input_path.write_text("# Test Document\n\nThis is a test.")
        output_path = tmp_path / "output" / "document.pdf"

        # Create the expected generated PDF
        generated_pdf = input_path.with_suffix(".pdf")
        generated_pdf.write_bytes(b"%PDF-1.4 test")

        handler.convert(input_path, output_path)

        # Verify subprocess was called
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert "md-to-pdf" in call_args[0][0]
        assert "--config-file" in call_args[0][0]

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_convert_handles_subprocess_error(
        self, mock_which: MagicMock, mock_run: MagicMock, tmp_path: Path
    ):
        """Test that subprocess errors are handled properly."""
        import subprocess

        mock_which.return_value = "/usr/local/bin/md-to-pdf"
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "md-to-pdf", stderr="Conversion failed"
        )

        handler = MdConverter(config_path=tmp_path / "config.js")

        input_path = tmp_path / "document.md"
        input_path.write_text("# Test Document")
        output_path = tmp_path / "output.pdf"

        with pytest.raises(ConversionError, match="Failed to convert"):
            handler.convert(input_path, output_path)

    def test_custom_config_path(self, tmp_path: Path):
        """Test that custom config path is used."""
        custom_config = tmp_path / "custom-config.js"
        custom_config.write_text("module.exports = {};")

        handler = MdConverter(config_path=custom_config)
        assert handler._config_path == custom_config

    def test_default_config_path_resolution(self):
        """Test that default config path is resolved correctly."""
        handler = MdConverter()
        # The config path should be set (either from resources or fallback)
        assert handler._config_path is not None

    @pytest.mark.skipif(
        shutil.which("md-to-pdf") is None, reason="md-to-pdf not installed"
    )
    def test_convert_real_md_fixture_no_errors(self, tmp_path: Path):
        """Test MD→PDF conversion completes without errors using sample.md fixture."""
        sample_md = FIXTURES_DIR / "sample.md"
        handler = MdConverter()
        output_path = tmp_path / "sample.pdf"

        handler.convert(sample_md, output_path)

        assert output_path.exists()
        with output_path.open("rb") as f:
            header = f.read(4)
            assert header == b"%PDF"
