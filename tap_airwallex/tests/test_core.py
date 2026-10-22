"""Tests standard tap features using the built-in SDK tests library."""

import datetime
import json
from unittest.mock import MagicMock, patch

import pytest
from hotglue_singer_sdk.testing import get_standard_tap_tests

from tap_airwallex.streams import AccountsStream
from tap_airwallex.tap import TapAirwallex

SAMPLE_CONFIG = {
    "start_date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
    "api_key": "test-api-key",
    "client_id": "test-client-id",
}


@pytest.mark.parametrize(
    "standard_tap_test",
    [
        test
        for test in get_standard_tap_tests(TapAirwallex, config=SAMPLE_CONFIG)
        if test.__name__ != "_test_stream_connections"
    ],
)
def test_standard_tap_features(standard_tap_test):
    """Run the SDK checks that do not require a live Airwallex account."""
    standard_tap_test()


def test_access_token_support_uses_sandbox_login_endpoint(tmp_path):
    """Access-token support obtains and persists the Airwallex login token."""
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({**SAMPLE_CONFIG, "is_sandbox": True}))
    tap = TapAirwallex(config=config_path)
    token_response = MagicMock()
    token_response.json.return_value = {
        "token": "airwallex-access-token",
        "expires_at": "2030-01-01T00:00:00+00:00",
    }

    with patch("tap_airwallex.auth.requests.post", return_value=token_response) as request_token:
        assert TapAirwallex.fetch_access_token(tap) == {
            "access_token": "airwallex-access-token"
        }

    assert request_token.call_args_list[0][0][0] == (
        "https://api-demo.airwallex.com/api/v1/authentication/login"
    )
    assert request_token.call_args_list[0][1]["headers"] == {
        "Content-Type": "application/json",
        "x-api-key": "test-api-key",
        "x-client-id": "test-client-id",
    }
    assert json.loads(config_path.read_text())["access_token"] == "airwallex-access-token"


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
