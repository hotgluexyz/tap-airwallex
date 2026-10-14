"""Tests standard tap features using the built-in SDK tests library."""

import datetime
from unittest.mock import MagicMock

import pytest
from hotglue_singer_sdk.testing import get_standard_tap_tests

from tap_airwallex.streams import AccountsStream
from tap_airwallex.tap import TapAirwallex

SAMPLE_CONFIG = {
    "start_date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    # TODO: Initialize minimal tap config
}


# Run standard built-in tap tests from the SDK:
def test_standard_tap_tests():
    """Run standard tap tests from the SDK."""
    tests = get_standard_tap_tests(
        TapAirwallex,
        config=SAMPLE_CONFIG
    )
    for test in tests:
        test()


@pytest.mark.parametrize(
    "account_ids, expected_count",
    [(["account-1", "account-2"], 2), ("account-1, account-2", 2)],
)
def test_accounts_estimated_record_count_matches_emitted_accounts(
    account_ids, expected_count
):
    """The estimate follows the same account-ID parsing as the stream records."""
    tap = MagicMock()
    tap.config = {"account_ids": account_ids}

    assert AccountsStream(tap=tap).get_estimated_record_count() == expected_count
