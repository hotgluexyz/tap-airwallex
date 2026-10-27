"""Tests standard tap features using the built-in SDK tests library."""

import datetime
import json
from unittest.mock import MagicMock, patch

import pytest
from hotglue_singer_sdk.testing import get_standard_tap_tests

from tap_airwallex.streams import AccountsStream
from tap_airwallex.tap import TapAirwallex

SAMPLE_CONFIG = {
    "start_date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    # TODO: Initialize minimal tap config
}


def test_standard_tap_tests():
    """Run standard tap tests from the SDK."""
    tests = get_standard_tap_tests(
        TapAirwallex,
        config=SAMPLE_CONFIG
    )
    for test in tests:
        test()


def test_access_token_support_uses_sandbox_login_endpoint(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "api_key": "test-api-key",
                "client_id": "test-client-id",
                "is_sandbox": True,
            }
        )
    )
    token_response = MagicMock()
    token_response.json.return_value = {
        "token": "airwallex-access-token",
        "expires_at": "2030-01-01T00:00:00+00:00",
    }

    with patch("tap_airwallex.auth.requests.post", return_value=token_response) as request_token:
        assert TapAirwallex.fetch_access_token(TapAirwallex(config=config_path)) == {
            "access_token": "airwallex-access-token"
        }

    assert request_token.call_args_list[0][0][0] == (
        "https://api-demo.airwallex.com/api/v1/authentication/login"
    )


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
