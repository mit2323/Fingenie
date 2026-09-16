import pytest
from app.core.config import settings


def test_app_name_is_set():
    assert settings.APP_NAME
    assert isinstance(settings.APP_NAME, str)


def test_app_version_is_set():
    assert settings.APP_VERSION


def test_database_url_is_configured():
    assert settings.DATABASE_URL
    assert "postgresql" in settings.DATABASE_URL