"""Stream type classes for tap-airwallex."""

from hotglue_singer_sdk import typing as th

from tap_airwallex.client import AirwallexStream
from typing import Any, Optional, Iterable
import requests
from typing import Dict, Any
from pendulum import parse

from tap_airwallex.schema_helpers import (
    _account_customer_agreements_type,
    _account_details_type,
    _account_primary_contact_type,
    _bill_attachment_type,
    _bill_line_item_type,
    _bill_payment_type,
    _transfer_beneficiary_type,
    _transfer_conversion_type,
    _transfer_funding_type,
    _transfer_payer_type,
)


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
        th.Property("amount", th.NumberType),
        th.Property("client_rate", th.NumberType),
        th.Property("currency_pair", th.StringType),
        th.Property("net", th.NumberType),
        th.Property("fee", th.NumberType),
        th.Property("estimated_settled_at", th.DateTimeType),
        th.Property("settled_at", th.DateTimeType),
        th.Property("description", th.StringType),
        th.Property("status", th.StringType),
        th.Property("created_at", th.DateTimeType),
        th.Property("legal_entity_id", th.StringType),
        th.Property("account_id", th.StringType),
    ).to_dict()


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


class TransfersStream(AirwallexStream):
    """Define custom stream."""

    name = "transfers"
    path = "/transfers"
    primary_keys = ["id"]
    parent_stream_type = AccountDetailsStream
    permission_type = "account"

    schema = th.PropertiesList(
        th.Property("amount_beneficiary_receives", th.NumberType),
        th.Property("amount_payer_pays", th.NumberType),
        th.Property("beneficiary", _transfer_beneficiary_type),
        th.Property("beneficiary_id", th.StringType),
        th.Property("conversion", _transfer_conversion_type),
        th.Property("created_at", th.DateTimeType),
        th.Property("fee_amount", th.NumberType),
        th.Property("fee_currency", th.StringType),
        th.Property("fee_paid_by", th.StringType),
        th.Property("funding", _transfer_funding_type),
        th.Property("id", th.StringType),
        th.Property("payer", _transfer_payer_type),
        th.Property("reason", th.StringType),
        th.Property("reference", th.StringType),
        th.Property("remarks", th.StringType),
        th.Property("request_id", th.StringType),
        th.Property("short_reference_id", th.StringType),
        th.Property("source_amount", th.NumberType),
        th.Property("source_currency", th.StringType),
        th.Property("status", th.StringType),
        th.Property("swift_charge_option", th.StringType),
        th.Property("transfer_amount", th.NumberType),
        th.Property("transfer_currency", th.StringType),
        th.Property("transfer_date", th.StringType),
        th.Property("transfer_method", th.StringType),
        th.Property("updated_at", th.DateTimeType),
    ).to_dict()

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        next_page_token = next_page_token or 0
        params["page"] = next_page_token
        return params

    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any]
    ) -> Optional[Any]:
        """Return a token for identifying next page or None if no more pages."""
        res_json = response.json()
        next_page_token = res_json.get("page_after")
        if next_page_token:
            return next_page_token