import pytest


@pytest.fixture(autouse=True)
def setup_unit_test(monkeypatch):
    """Set up environment variables for all unit tests."""
    monkeypatch.setenv("DCV_APP_NAME", "dcv-test")
    monkeypatch.setenv("DCV_OUTPUT_DIR", "test_output")
