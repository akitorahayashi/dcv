"""Integration tests for the DI container."""

from typer.testing import CliRunner

from dcv.main import app


class TestContainerIntegration:
    """Integration tests for the DI container."""

    def test_container_initializes_with_defaults(self, cli_runner: CliRunner):
        """Test that the container initializes correctly."""
        result = cli_runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert "dcv" in result.output
