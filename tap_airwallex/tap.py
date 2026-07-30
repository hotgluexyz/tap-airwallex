"""airwallex tap class."""

from typing import List

from hotglue_singer_sdk import Tap, Stream
from hotglue_singer_sdk import typing as th  
from tap_airwallex.streams import (
    AccountsStream,
    AccountDetailsStream,
    FinancialTransactionsStream,
    BillsStream,
    TransfersStream,
    ExpensesStream,
    IssuingTransactionsStream,
    DirectDebitsStream,
    DepositsStream,
    ConversionsStream,
)
STREAM_TYPES = [
    FinancialTransactionsStream,
    BillsStream,
    AccountsStream,
    AccountDetailsStream,
    TransfersStream,
    ExpensesStream,
    IssuingTransactionsStream,
    DirectDebitsStream,
    DepositsStream,
    ConversionsStream,
]


class Tapairwallex(Tap):
    """airwallex tap class."""
    name = "tap-airwallex"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_key",
            th.StringType,
            required=True,
            description="The token to request a token from the API service"
        ),
        th.Property(
            "client_id",
            th.StringType,
            required=True,
            description="Client ID to request a token from the API service"
        ),
        th.Property(
            "is_sandbox",
            th.BooleanType,
            default=False,
            description="Whether to use the sandbox environment"
        )
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]


if __name__ == "__main__":
    Tapairwallex.cli()