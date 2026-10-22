"""Tests for the outcomePrices parsing helper.

The Gamma API returns ``outcomePrices`` as a double-encoded JSON list
(``'["0.92", "0.08"]'``), but a ``{"Yes": ..., "No": ...}`` mapping is also
seen in older/cached payloads. Both must parse to the same numbers, and
anything malformed must degrade to a neutral 0.5/0.5 rather than raising.
"""

import pytest

from app.services.polymarket import parse_yes_no_prices


class TestParseYesNoPricesHandlesListForm:
    """The list form is what the live Gamma API returns."""

    def test_parses_positional_list(self) -> None:
        assert parse_yes_no_prices(["0.92", "0.08"]) == (0.92, 0.08)

    def test_parses_json_encoded_list(self) -> None:
        assert parse_yes_no_prices('["0.92", "0.08"]') == (0.92, 0.08)

    def test_parses_numeric_list(self) -> None:
        assert parse_yes_no_prices([0.92, 0.08]) == (0.92, 0.08)

    def test_parses_list_with_extra_entries(self) -> None:
        assert parse_yes_no_prices(["0.60", "0.40", "0.00"]) == (0.60, 0.40)


class TestParseYesNoPricesHandlesDictForm:
    """Legacy/cached payloads use a Yes/No mapping."""

    def test_parses_dict(self) -> None:
        assert parse_yes_no_prices({"Yes": "0.60", "No": "0.40"}) == (0.60, 0.40)

    def test_parses_json_encoded_dict(self) -> None:
        assert parse_yes_no_prices('{"Yes": "0.60", "No": "0.40"}') == (0.60, 0.40)

    def test_missing_keys_default_to_half(self) -> None:
        assert parse_yes_no_prices({"Yes": "0.60"}) == (0.60, 0.5)


class TestParseYesNoPricesDegradesGracefully:
    """Malformed input must never raise - the caller gets neutral odds."""

    @pytest.mark.parametrize(
        "payload",
        [
            None,
            "",
            "not json",
            [],
            ["0.92"],
            {},
            {"Yes": "abc", "No": "def"},
            ["abc", "def"],
            42,
        ],
    )
    def test_unrecognised_payloads_return_neutral(self, payload: object) -> None:
        assert parse_yes_no_prices(payload) == (0.5, 0.5)

    def test_null_entries_become_half(self) -> None:
        assert parse_yes_no_prices([None, None]) == (0.5, 0.5)
        assert parse_yes_no_prices({"Yes": None, "No": None}) == (0.5, 0.5)
