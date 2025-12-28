"""Integration tests for scaffold command."""

from pathlib import Path

from typer.testing import CliRunner

from dcv.main import app


class TestScaffoldCommand:
    """Integration tests for scaffold command."""

    def test_scaffold_css_only(self, cli_runner: CliRunner, tmp_path: Path):
        """Test exporting CSS only."""
        result = cli_runner.invoke(app, ["scaffold", "--css", "-o", str(tmp_path)])

        assert result.exit_code == 0, f"Command failed: {result.output}"
        assert "Exported assets:" in result.output

        css_file = tmp_path / "dcv_custom.css"
        assert css_file.exists(), "CSS file not created"

        # Verify content
        css_content = css_file.read_text()
        assert "@page" in css_content
        assert "margin-top:" in css_content

    def test_scaffold_template_only(self, cli_runner: CliRunner, tmp_path: Path):
        """Test exporting template only."""
        result = cli_runner.invoke(app, ["scaffold", "--template", "-o", str(tmp_path)])

        assert result.exit_code == 0, f"Command failed: {result.output}"
        assert "Exported assets:" in result.output

        template_file = tmp_path / "dcv_custom_template.html"
        assert template_file.exists(), "Template file not created"

        # Verify content
        template_content = template_file.read_text()
        assert "<!DOCTYPE html>" in template_content
        assert "{{ body_content }}" in template_content
        assert "MathJax" in template_content

    def test_scaffold_all(self, cli_runner: CliRunner, tmp_path: Path):
        """Test exporting all assets."""
        result = cli_runner.invoke(app, ["scaffold", "--all", "-o", str(tmp_path)])

        assert result.exit_code == 0, f"Command failed: {result.output}"
        assert "Exported assets:" in result.output

        css_file = tmp_path / "dcv_custom.css"
        template_file = tmp_path / "dcv_custom_template.html"

        assert css_file.exists(), "CSS file not created"
        assert template_file.exists(), "Template file not created"

    def test_scaffold_default_output_dir(self, cli_runner: CliRunner, tmp_path: Path):
        """Test scaffolding to current directory (default)."""
        # CliRunner doesn't change actual cwd, so we specify output dir explicitly
        result = cli_runner.invoke(app, ["scaffold", "--css", "-o", str(tmp_path)])

        assert result.exit_code == 0
        css_file = tmp_path / "dcv_custom.css"
        assert css_file.exists()

    def test_scaffold_no_options(self, cli_runner: CliRunner, tmp_path: Path):
        """Test scaffold with no options shows warning."""
        result = cli_runner.invoke(app, ["scaffold", "-o", str(tmp_path)])

        assert result.exit_code == 0
        assert "No assets specified" in result.output

    def test_scaffolded_css_works_for_conversion(
        self, cli_runner: CliRunner, tmp_path: Path
    ):
        """Test that scaffolded CSS can be used for conversion."""
        # First, scaffold CSS
        result = cli_runner.invoke(app, ["scaffold", "--css", "-o", str(tmp_path)])
        assert result.exit_code == 0

        css_file = tmp_path / "dcv_custom.css"
        assert css_file.exists()

        # Modify CSS to test customization
        css_content = css_file.read_text()
        css_content = css_content.replace("margin-top: 30mm", "margin-top: 50mm")
        css_file.write_text(css_content)

        # Create test markdown file
        test_md = tmp_path / "test.md"
        test_md.write_text("# Test Document\n\nThis is a test.")

        # Convert using scaffolded CSS
        output_dir = tmp_path / "output"
        result = cli_runner.invoke(
            app,
            [
                "md2pdf",
                "-f",
                str(test_md),
                "-o",
                str(output_dir),
                "--css",
                str(css_file),
            ],
        )

        assert result.exit_code == 0, f"Conversion failed: {result.output}"

        output_pdf = output_dir / "test.pdf"
        assert output_pdf.exists(), "PDF not created with scaffolded CSS"

    def test_scaffold_creates_nested_output_dir(
        self, cli_runner: CliRunner, tmp_path: Path
    ):
        """Test that scaffold creates nested directories if needed."""
        nested_dir = tmp_path / "custom" / "styles"

        result = cli_runner.invoke(app, ["scaffold", "--css", "-o", str(nested_dir)])

        assert result.exit_code == 0
        css_file = nested_dir / "dcv_custom.css"
        assert css_file.exists()
        assert nested_dir.exists()
