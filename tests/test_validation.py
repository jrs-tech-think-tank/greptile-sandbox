"""Tests for URL validation and normalization."""

import pytest

from app.validation import InvalidURLError, is_valid_url, normalize_url


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("http://Example.com", "http://example.com"),
        ("https://EXAMPLE.com/Path?q=1", "https://example.com/Path?q=1"),
        ("  https://example.com/x  ", "https://example.com/x"),
        ("https://example.com/a#frag", "https://example.com/a"),
    ],
)
def test_normalize_url_ok(raw, expected):
    assert normalize_url(raw) == expected


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "   ",
        "ftp://example.com",
        "example.com",
        "http://",
        "javascript:alert(1)",
    ],
)
def test_normalize_url_rejects_bad_input(raw):
    with pytest.raises(InvalidURLError):
        normalize_url(raw)


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("http://example.com:80/x", "http://example.com/x"),
        ("https://example.com:443/x", "https://example.com/x"),
        ("http://example.com:8080/x", "http://example.com:8080/x"),
    ],
)
def test_normalize_url_strips_default_ports(raw, expected):
    assert normalize_url(raw) == expected


def test_is_valid_url():
    assert is_valid_url("https://example.com")
    assert not is_valid_url("not a url")
