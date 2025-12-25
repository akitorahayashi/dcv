import pytest


@pytest.fixture(autouse=True)
def mock_env_for_integration_tests(monkeypatch):
    """Set up environment variables for all integration tests."""
    monkeypatch.setenv("DCV_APP_NAME", "dcv-test")
    monkeypatch.setenv("DCV_OUTPUT_DIR", "test_output")
