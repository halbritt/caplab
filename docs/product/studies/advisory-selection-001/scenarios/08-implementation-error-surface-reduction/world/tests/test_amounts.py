import pytest

from ledgerline.amounts import parse_amount


def test_plain_amount():
    assert parse_amount("1234.56") == 123456


def test_thousands_separator_and_symbol():
    assert parse_amount("$1,200.00") == 120000


def test_parenthesised_negative():
    assert parse_amount("(45.10)") == -4510


def test_dr_trailer_is_negative():
    assert parse_amount("12.00 DR") == -1200


def test_cr_trailer_is_positive():
    assert parse_amount("12.00 CR") == 1200


def test_garbage_raises_value_error():
    with pytest.raises(ValueError):
        parse_amount("see statement")
