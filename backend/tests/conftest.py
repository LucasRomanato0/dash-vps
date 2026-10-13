import pytest

from app.config import get_settings
from app.main import app


@pytest.fixture(autouse=True)
def reset_fastapi_test_state():
    """Keep cached settings and dependency overrides isolated per test."""
    app.dependency_overrides.clear()
    get_settings.cache_clear()
    yield
    app.dependency_overrides.clear()
    get_settings.cache_clear()
