"""Short code generation.

Generates random, URL-safe base62 codes using the ``secrets`` module so
codes are not predictable.
"""

from __future__ import annotations

import secrets

ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
DEFAULT_LENGTH = 7


def generate_short_code(length: int = DEFAULT_LENGTH) -> str:
    """Return a random base62 short code of ``length`` characters."""
    if length < 1:
        raise ValueError("length must be at least 1")
    return "".join(secrets.choice(ALPHABET) for _ in range(length))
