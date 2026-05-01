import pytest
from app.utils.fuzzy import is_fuzzy_match, levenshtein_distance


def test_exact_match():
    assert levenshtein_distance("abc", "abc") == 0


def test_single_insertion():
    assert levenshtein_distance("abc", "abcd") == 1


def test_single_deletion():
    assert levenshtein_distance("abcd", "abc") == 1


def test_single_substitution():
    assert levenshtein_distance("abc", "axc") == 1


def test_transposition():
    assert levenshtein_distance("ab", "ba") == 2


def test_empty_strings():
    assert levenshtein_distance("", "") == 0


def test_one_empty():
    assert levenshtein_distance("abc", "") == 3
    assert levenshtein_distance("", "abc") == 3


def test_fuzzy_match_within_threshold():
    assert is_fuzzy_match("halabi", "jalabi", threshold=1) is True


def test_fuzzy_match_exceeds_threshold():
    assert is_fuzzy_match("halabi", "xyz", threshold=3) is False


def test_fuzzy_match_case_insensitive():
    assert is_fuzzy_match("Halabi", "halabi", threshold=0) is True


def test_fuzzy_match_default_threshold():
    assert is_fuzzy_match("mendoza beatriz", "mendoza beatris") is True
