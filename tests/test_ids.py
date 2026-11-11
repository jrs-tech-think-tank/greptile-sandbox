"""Tests for short code generation."""

import pytest

from app.ids import ALPHABET, DEFAULT_LENGTH, generate_short_code


def test_default_length_and_alphabet():
    code = generate_short_code()
    assert len(code) == DEFAULT_LENGTH
    assert all(ch in ALPHABET for ch in code)


def test_custom_length():
    assert len(generate_short_code(12)) == 12


def test_invalid_length():
    with pytest.raises(ValueError):
        generate_short_code(0)


def test_codes_are_reasonably_unique():
    codes = {generate_short_code() for _ in range(1000)}
    # With a 7-char base62 code, 1000 draws should not collide in practice.
    assert len(codes) == 1000
