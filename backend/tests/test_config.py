"""Tests for application settings and configuration parsing."""

import os
from app.config import Settings


def test_cors_origins_default():
    """Verify default CORS origins are loaded when no env var is set."""
    if "CORS_ORIGINS" in os.environ:
        del os.environ["CORS_ORIGINS"]

    settings = Settings()
    assert isinstance(settings.CORS_ORIGINS, list)
    assert "http://localhost:3000" in settings.CORS_ORIGINS
    assert "http://127.0.0.1:3000" in settings.CORS_ORIGINS


def test_cors_origins_comma_separated(monkeypatch):
    """Verify comma-separated string in env var is properly parsed into a list."""
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,https://civicpilot.gov.in")
    settings = Settings()
    assert isinstance(settings.CORS_ORIGINS, list)
    assert settings.CORS_ORIGINS == [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://civicpilot.gov.in",
    ]


def test_cors_origins_json_array(monkeypatch):
    """Verify JSON array string in env var is properly parsed into a list."""
    monkeypatch.setenv("CORS_ORIGINS", '["http://localhost:3000", "http://127.0.0.1:3000"]')
    settings = Settings()
    assert isinstance(settings.CORS_ORIGINS, list)
    assert settings.CORS_ORIGINS == [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


def test_cors_origins_single_quoted_array(monkeypatch):
    """Verify single-quoted array string in env var is gracefully parsed."""
    monkeypatch.setenv("CORS_ORIGINS", "['http://localhost:3000', 'http://127.0.0.1:3000']")
    settings = Settings()
    assert isinstance(settings.CORS_ORIGINS, list)
    assert settings.CORS_ORIGINS == [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


def test_cors_origins_single_origin(monkeypatch):
    """Verify single origin string is parsed as a single-element list."""
    monkeypatch.setenv("CORS_ORIGINS", "https://example.com")
    settings = Settings()
    assert isinstance(settings.CORS_ORIGINS, list)
    assert settings.CORS_ORIGINS == ["https://example.com"]


def test_cors_origins_empty_string(monkeypatch):
    """Verify empty string results in an empty list."""
    monkeypatch.setenv("CORS_ORIGINS", "")
    settings = Settings()
    assert isinstance(settings.CORS_ORIGINS, list)
    assert settings.CORS_ORIGINS == []
