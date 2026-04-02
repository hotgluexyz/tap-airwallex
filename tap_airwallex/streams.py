"""Stream type classes for tap-airwallex."""

from hotglue_singer_sdk import typing as th

from tap_airwallex.client import AirwallexStream

class FinancialTransactionsStream(AirwallexStream):
    """Define custom stream."""
    name = "financial_transactions"
    path = "/financial_transactions"
    primary_keys = ["id"]
    replication_key = "created_at"
    replication_key_filter_field = "from_created_at"
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("batch_id", th.StringType),
        th.Property("source_id", th.StringType),
        th.Property("funding_source_id", th.StringType),
        th.Property("source_type", th.StringType),
        th.Property("transaction_type", th.StringType),
        th.Property("currency", th.StringType),
        th.Property("amount", th.IntegerType),
        th.Property("client_rate", th.NumberType),
        th.Property("currency_pair", th.StringType),
        th.Property("net", th.IntegerType),
        th.Property("fee", th.IntegerType),
        th.Property("estimated_settled_at", th.DateTimeType),
        th.Property("settled_at", th.DateTimeType),
        th.Property("description", th.StringType),
        th.Property("status", th.StringType),
        th.Property("created_at", th.DateTimeType),
    ).to_dict()
