"""URL validation and normalization.

Kept deliberately small: we accept http/https URLs that have a network
location (host), normalize the scheme/host to lowercase, and strip empty
fragments. Anything else is rejected with a clear error.
"""

from __future__ import annotations

from urllib.parse import urlsplit, urlunsplit

ALLOWED_SCHEMES = ("http", "https")


class InvalidURLError(ValueError):
    """Raised when a URL fails validation."""


def normalize_url(raw: str) -> str:
    """Validate ``raw`` and return a normalized form.

    Raises :class:`InvalidURLError` if the URL is not a well-formed
    http(s) URL with a host.
    """
    if not isinstance(raw, str):
        raise InvalidURLError("URL must be a string")

    candidate = raw.strip()
    if not candidate:
        raise InvalidURLError("URL must not be empty")

    parts = urlsplit(candidate)

    scheme = parts.scheme.lower()
    if scheme not in ALLOWED_SCHEMES:
        raise InvalidURLError(
            f"URL scheme must be one of {ALLOWED_SCHEMES}, got {parts.scheme!r}"
        )

    if not parts.netloc:
        raise InvalidURLError("URL must include a host")

    # Lowercase the host portion but preserve any userinfo/port as given.
    netloc = parts.netloc.lower()

    normalized = urlunsplit((scheme, netloc, parts.path, parts.query, ""))
    return normalized


def is_valid_url(raw: str) -> bool:
    """Return True if ``raw`` is a valid http(s) URL."""
    try:
        normalize_url(raw)
    except InvalidURLError:
        return False
    return True
