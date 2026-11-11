"""Tests for the SQLite storage layer."""

import pytest

from app import storage


def test_create_and_get(db_path):
    link = storage.create_link("abc1234", "https://example.com", db_path)
    assert link.code == "abc1234"
    assert link.hits == 0

    fetched = storage.get_link("abc1234", db_path)
    assert fetched is not None
    assert fetched.url == "https://example.com"


def test_get_missing_returns_none(db_path):
    assert storage.get_link("missing", db_path) is None


def test_duplicate_code_raises(db_path):
    storage.create_link("dup1234", "https://example.com", db_path)
    with pytest.raises(storage.DuplicateCodeError):
        storage.create_link("dup1234", "https://other.com", db_path)


def test_list_newest_first(db_path):
    storage.create_link("aaa1111", "https://a.com", db_path)
    storage.create_link("bbb2222", "https://b.com", db_path)
    codes = [link.code for link in storage.list_links(db_path)]
    assert set(codes) == {"aaa1111", "bbb2222"}


def test_count_links(db_path):
    assert storage.count_links(db_path) == 0
    storage.create_link("cnt1111", "https://a.com", db_path)
    storage.create_link("cnt2222", "https://b.com", db_path)
    assert storage.count_links(db_path) == 2


def test_delete(db_path):
    storage.create_link("del1234", "https://example.com", db_path)
    assert storage.delete_link("del1234", db_path) is True
    assert storage.delete_link("del1234", db_path) is False
    assert storage.get_link("del1234", db_path) is None


def test_record_hit(db_path):
    storage.create_link("hit1234", "https://example.com", db_path)
    storage.record_hit("hit1234", db_path)
    storage.record_hit("hit1234", db_path)
    assert storage.get_link("hit1234", db_path).hits == 2
