"""Stream type classes for tap-airwallex."""

from hotglue_singer_sdk import typing as th

from tap_airwallex.client import AirwallexStream
from typing import Any, Optional, Iterable
import requests
from typing import Dict, Any

from tap_airwallex.schema_helpers import _account_details_type, _account_customer_agreements_type, _account_primary_contact_type, _bill_attachment_type, _bill_payment_type, _bill_line_item_type
from pendulum import parse

class AccountsStream(AirwallexStream):
    """Define custom stream."""

    name = "accounts"
    path = "/"
    primary_keys = ["id"]
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
    ).to_dict()

    def get_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Return a list of records."""
        account_ids = self.config.get("account_ids", [])
        if isinstance(account_ids, str):
            account_ids = account_ids.split(",")
            account_ids = [account_id.strip() for account_id in account_ids]

        for account_id in account_ids:
            yield {"id": account_id}

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a dictionary of values to be used in child context."""
        return {
            "account_id": record["id"]
        }

class AccountDetailsStream(AirwallexStream):
    """Define custom stream."""

    name = "account_details"
    path = "/account"
    primary_keys = ["id"]
    records_jsonpath = "$.[*]"
    parent_stream_type = AccountsStream
    permission_type = "account"

    schema = th.PropertiesList(
        th.Property("account_details", _account_details_type),
        th.Property("created_at", th.DateTimeType),
        th.Property("customer_agreements", _account_customer_agreements_type),
        th.Property("id", th.StringType),
        th.Property("nickname", th.StringType),
        th.Property("primary_contact", _account_primary_contact_type),
        th.Property("status", th.StringType),
        th.Property("view_type", th.StringType),
    ).to_dict()

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a dictionary of values to be used in child context."""
        return {
            "legal_entity_id": record["account_details"]["legal_entity_id"],
            "account_id": context.get("account_id")
        }


class FinancialTransactionsStream(AirwallexStream):
    """Define custom stream."""

    name = "financial_transactions"
    path = "/financial_transactions"
    primary_keys = ["id"]
    parent_stream_type = AccountDetailsStream
    permission_type = "account"

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
        th.Property("legal_entity_id", th.StringType),
        th.Property("account_id", th.StringType),
    ).to_dict()

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params = super().get_url_params(context, next_page_token)
        if self.config.get("financial_transactions_start_date"):
            params["from_created_at"] = parse(self.config.get("financial_transactions_start_date")).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        return params

class BillsStream(AirwallexStream):
    """Define custom stream."""

    name = "bills"
    path = "/spend/bills"
    primary_keys = ["id"]
    replication_key = "created_at"
    replication_key_filter_field = "from_created_at"
    permission_type = "organization"

    schema = th.PropertiesList(
        th.Property("approvers", th.ArrayType(th.StringType)),
        th.Property("attachments", th.ArrayType(_bill_attachment_type)),
        th.Property("bill_payments", th.ArrayType(_bill_payment_type)),
        th.Property("billing_amount", th.StringType),
        th.Property("billing_currency", th.StringType),
        th.Property("created_at", th.DateTimeType),
        th.Property("description", th.StringType),
        th.Property("due_date", th.DateTimeType),
        th.Property("external_id", th.StringType),
        th.Property("id", th.StringType),
        th.Property("invoice_number", th.StringType),
        th.Property("issued_date", th.DateTimeType),
        th.Property("legal_entity_id", th.StringType),
        th.Property("line_items", th.ArrayType(_bill_line_item_type)),
        th.Property("purchase_order_id", th.StringType),
        th.Property("status", th.StringType),
        th.Property("sync_error_message", th.StringType),
        th.Property("sync_status", th.StringType),
        th.Property("tax_status", th.StringType),
        th.Property("updated_at", th.DateTimeType),
        th.Property("vendor_id", th.StringType),
    ).to_dict()

    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any]
    ) -> Optional[Any]:
        """Return a token for identifying next page or None if no more pages."""
        previous_token = previous_token or 0
        res_json = response.json()
        next_page_token = res_json.get("page_after")
        return next_page_token

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key and self.replication_key_filter_field:
            start_date = self.get_starting_time(context)
            params[self.replication_key_filter_field] = start_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        return params