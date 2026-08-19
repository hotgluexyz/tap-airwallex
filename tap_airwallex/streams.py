"""Stream type classes for tap-airwallex."""

from hotglue_singer_sdk import typing as th

from tap_airwallex.client import AirwallexStream, SpendStream, DateRangeStream
from typing import Any, Optional, Iterable, Dict
import requests
from datetime import datetime, timezone

from tap_airwallex.schema_helpers import (
    _account_customer_agreements_type,
    _account_details_type,
    _account_primary_contact_type,
    _bill_accounting_field_selection_type,
    _bill_attachment_type,
    _bill_line_item_type,
    _bill_payment_type,
    _expense_card_transaction_type,
    _expense_comment_type,
    _expense_line_item_type,
    _issuing_transaction_card_transaction_data_type,
    _issuing_transaction_merchant_type,
    _issuing_transaction_risk_details_type,
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
    primary_keys = ["id", "transaction_type"]
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


class BillsStream(SpendStream):
    """Define custom stream."""

    name = "bills"
    path = "/spend/bills"
    primary_keys = ["id"]
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


class ExpensesStream(SpendStream):
    """Define expenses stream."""

    name = "expenses"
    path = "/spend/expenses"
    primary_keys = ["id"]
    permission_type = "organization"

    schema = th.PropertiesList(
        th.Property("account_id", th.StringType),
        th.Property(
            "accounting_field_selections",
            th.ArrayType(_bill_accounting_field_selection_type),
        ),
        th.Property("approvers", th.ArrayType(th.StringType)),
        th.Property("attachments", th.ArrayType(_bill_attachment_type)),
        th.Property("attendees", th.ArrayType(th.ObjectType())),
        th.Property("billing_amount", th.StringType),
        th.Property("billing_currency", th.StringType),
        th.Property("card_id", th.StringType),
        th.Property("card_transaction", _expense_card_transaction_type),
        th.Property("comments", th.ArrayType(_expense_comment_type)),
        th.Property("created_at", th.DateTimeType),
        th.Property("description", th.StringType),
        th.Property("id", th.StringType),
        th.Property("legal_entity_id", th.StringType),
        th.Property("line_items", th.ArrayType(_expense_line_item_type)),
        th.Property("merchant", th.StringType),
        th.Property("settled_at", th.DateTimeType),
        th.Property("status", th.StringType),
        th.Property("sync_status", th.StringType),
        th.Property("updated_at", th.DateTimeType),
    ).to_dict()


class IssuingTransactionsStream(DateRangeStream):
    """Define issuing transactions stream."""

    name = "issuing_transactions"
    path = "/issuing/transactions"
    primary_keys = ["transaction_id"]
    parent_stream_type = AccountDetailsStream
    permission_type = "account"
    # Airwallex allows page_num 0..100; page_num 101 returns EXCEED_MAX_PAGE_NUMBER.
    max_page_num = 100

    schema = th.PropertiesList(
        th.Property("acquiring_institution_identifier", th.StringType),
        th.Property("auth_code", th.StringType),
        th.Property("billing_amount", th.NumberType),
        th.Property("billing_currency", th.StringType),
        th.Property("card_id", th.StringType),
        th.Property("card_nickname", th.StringType),
        th.Property(
            "card_transaction_data",
            _issuing_transaction_card_transaction_data_type,
        ),
        th.Property("lifecycle_id", th.StringType),
        th.Property("masked_card_number", th.StringType),
        th.Property("merchant", _issuing_transaction_merchant_type),
        th.Property("network_transaction_id", th.StringType),
        th.Property("posted_date", th.DateTimeType),
        th.Property("retrieval_ref", th.StringType),
        th.Property("risk_details", _issuing_transaction_risk_details_type),
        th.Property("status", th.StringType),
        th.Property("transaction_amount", th.NumberType),
        th.Property("transaction_currency", th.StringType),
        th.Property("transaction_date", th.DateTimeType),
        th.Property("transaction_id", th.StringType),
        th.Property("transaction_type", th.StringType),
        th.Property("legal_entity_id", th.StringType),
        th.Property("account_id", th.StringType),
    ).to_dict()


class DirectDebitsStream(AirwallexStream):
    """Define direct debits stream."""

    name = "direct_debits"
    path = "/direct_debits"
    primary_keys = ["transaction_id"]
    permission_type = "account"
    parent_stream_type = AccountDetailsStream

    schema = th.PropertiesList(
        th.Property("amount", th.NumberType),
        th.Property("created_at", th.DateTimeType),
        th.Property("currency", th.StringType),
        th.Property("debtor_name", th.StringType),
        th.Property("global_account_id", th.StringType),
        th.Property("mandate_id", th.StringType),
        th.Property("statement_ref", th.StringType),
        th.Property("status", th.StringType),
        th.Property("transaction_id", th.StringType),
    ).to_dict()


class DepositsStream(DateRangeStream):
    """Define deposits stream."""

    name = "deposits"
    path = "/deposits"
    primary_keys = ["id"]
    permission_type = "account"
    parent_stream_type = AccountDetailsStream

    schema = th.PropertiesList(
        th.Property("amount", th.NumberType),
        th.Property("created_at", th.DateTimeType),
        th.Property("currency", th.StringType),
        th.Property("estimated_settled_at", th.DateTimeType),
        th.Property(
            "failure_details",
            th.CustomType({"type": ["object", "string"]}),
        ),
        th.Property(
            "fee",
            th.ObjectType(
                th.Property("amount", th.NumberType),
                th.Property("currency", th.StringType),
            ),
        ),
        th.Property("funding_source_id", th.StringType),
        th.Property("global_account_id", th.StringType),
        th.Property("id", th.StringType),
        th.Property(
            "payer",
            th.CustomType({"type": ["object", "string"]}),
        ),
        th.Property("provider_transaction_id", th.StringType),
        th.Property("reference", th.StringType),
        th.Property("settled_at", th.DateTimeType),
        th.Property("status", th.StringType),
        th.Property("type", th.StringType),
    ).to_dict()

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        next_page_token = next_page_token or 0
        params = super().get_url_params(context, next_page_token)
        return params


class ConversionsStream(AirwallexStream):
    """Define FX conversions stream."""

    name = "conversions"
    path = "/fx/conversions"
    primary_keys = ["conversion_id"]
    replication_key = "created_at"
    replication_key_filter_field = "from_created_at"
    permission_type = "account"
    parent_stream_type = AccountDetailsStream

    schema = th.PropertiesList(
        th.Property(
            "application_fee_options",
            th.ArrayType(
                th.ObjectType(
                    th.Property("amount", th.StringType),
                    th.Property("currency", th.StringType),
                    th.Property(
                        "metadata",
                        th.CustomType({"type": ["object", "string"]}),
                    ),
                    th.Property("percentage", th.StringType),
                    th.Property("source_type", th.StringType),
                    th.Property("type", th.StringType),
                )
            ),
        ),
        th.Property(
            "application_fees",
            th.ArrayType(
                th.ObjectType(
                    th.Property("amount", th.StringType),
                    th.Property("currency", th.StringType),
                    th.Property("source_type", th.StringType),
                )
            ),
        ),
        th.Property("awx_rate", th.NumberType),
        th.Property("buy_amount", th.NumberType),
        th.Property("buy_currency", th.StringType),
        th.Property("client_rate", th.NumberType),
        th.Property("conversion_date", th.StringType),
        th.Property("conversion_id", th.StringType),
        th.Property("created_at", th.DateTimeType),
        th.Property("currency_pair", th.StringType),
        th.Property("dealt_currency", th.StringType),
        th.Property(
            "funding",
            th.ObjectType(
                th.Property("debit_type", th.StringType),
                th.Property("failure_reason", th.StringType),
                th.Property("funding_source_id", th.StringType),
                th.Property("status", th.StringType),
            ),
        ),
        th.Property(
            "funding_source",
            th.ObjectType(
                th.Property("debit_type", th.StringType),
                th.Property("id", th.StringType),
            ),
        ),
        th.Property("mid_rate", th.NumberType),
        th.Property("quote_id", th.StringType),
        th.Property(
            "rate_details",
            th.ArrayType(
                th.ObjectType(
                    th.Property("buy_amount", th.NumberType),
                    th.Property("level", th.StringType),
                    th.Property("rate", th.NumberType),
                    th.Property("sell_amount", th.NumberType),
                )
            ),
        ),
        th.Property("request_id", th.StringType),
        th.Property("sell_amount", th.NumberType),
        th.Property("sell_currency", th.StringType),
        th.Property("settlement_cutoff_at", th.DateTimeType),
        th.Property("short_reference_id", th.StringType),
        th.Property("status", th.StringType),
        th.Property("updated_at", th.DateTimeType),
    ).to_dict()

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params = super().get_url_params(context, next_page_token)
        params["from_created_at"] = self.get_starting_time(context).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        params["to_created_at"] = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        return params


class PaymentDisputesStream(AirwallexStream):
    """Define payment disputes stream."""

    name = "payment_disputes"
    path = "/pa/payment_disputes"
    primary_keys = ["id"]
    permission_type = "account"
    replication_key_filter_field = "from_updated_at"
    replication_key = "updated_at"
    pagination_page_field = "page"
    page_size_field = "size"
    parent_stream_type = AccountDetailsStream

    schema = th.PropertiesList(
        th.Property(
            "accept_details",
            th.ArrayType(
                th.ObjectType(
                    th.Property("accepted_at", th.DateTimeType),
                    th.Property("accepted_by", th.StringType),
                    th.Property("description", th.StringType),
                    th.Property("reason", th.StringType),
                    th.Property(
                        "refund",
                        th.ObjectType(
                            th.Property("amount", th.NumberType),
                            th.Property("reason", th.StringType),
                        ),
                    ),
                    th.Property("stage", th.StringType),
                )
            ),
        ),
        th.Property("acquirer_reference_number", th.StringType),
        th.Property(
            "ai_dispute_automation",
            th.ObjectType(
                th.Property(
                    "recommendation",
                    th.ObjectType(
                        th.Property("action", th.StringType),
                        th.Property(
                            "evidence_to_submit",
                            th.ArrayType(th.StringType),
                        ),
                    ),
                ),
                th.Property("status", th.StringType),
                th.Property("unavailable_reason", th.StringType),
            ),
        ),
        th.Property("amount", th.NumberType),
        th.Property("card_brand", th.StringType),
        th.Property(
            "challenge_details",
            th.ArrayType(
                th.ObjectType(
                    th.Property("challenge_method", th.StringType),
                    th.Property("challenged_at", th.DateTimeType),
                    th.Property("challenged_by", th.StringType),
                    th.Property(
                        "customer_info",
                        th.ObjectType(
                            th.Property("billing_address", th.StringType),
                            th.Property("device_id", th.StringType),
                            th.Property("email", th.StringType),
                            th.Property("ip", th.StringType),
                            th.Property("name", th.StringType),
                            th.Property("phone_number", th.StringType),
                        ),
                    ),
                    th.Property(
                        "delivery_info",
                        th.ObjectType(
                            th.Property("address", th.StringType),
                            th.Property("delivered_at", th.DateTimeType),
                            th.Property("fee_amount", th.NumberType),
                            th.Property("fee_currency", th.StringType),
                            th.Property("name", th.StringType),
                            th.Property("phone_number", th.StringType),
                            th.Property("shipped_at", th.DateTimeType),
                            th.Property("shipping_company", th.StringType),
                            th.Property("shipping_method", th.StringType),
                            th.Property("status", th.StringType),
                            th.Property("tracking_number", th.StringType),
                        ),
                    ),
                    th.Property(
                        "evidence",
                        th.CustomType({"type": ["object", "string"]}),
                    ),
                    th.Property(
                        "order_info",
                        th.ObjectType(
                            th.Property("created_at", th.DateTimeType),
                            th.Property("id", th.StringType),
                            th.Property("invoice_number", th.StringType),
                            th.Property(
                                "products",
                                th.ArrayType(
                                    th.ObjectType(
                                        th.Property("category", th.StringType),
                                        th.Property("code", th.StringType),
                                        th.Property("desc", th.StringType),
                                        th.Property("effective_end_at", th.StringType),
                                        th.Property(
                                            "effective_start_at", th.StringType
                                        ),
                                        th.Property("image_url", th.StringType),
                                        th.Property("name", th.StringType),
                                        th.Property("quantity", th.IntegerType),
                                        th.Property(
                                            "seller",
                                            th.ObjectType(
                                                th.Property(
                                                    "identifier", th.StringType
                                                ),
                                                th.Property("name", th.StringType),
                                            ),
                                        ),
                                        th.Property("sku", th.StringType),
                                        th.Property("type", th.StringType),
                                        th.Property("unit_price", th.NumberType),
                                        th.Property("url", th.StringType),
                                    )
                                ),
                            ),
                            th.Property("total_amount", th.NumberType),
                            th.Property("total_currency", th.StringType),
                        ),
                    ),
                    th.Property("product_description", th.StringType),
                    th.Property("product_type", th.StringType),
                    th.Property("reason", th.StringType),
                    th.Property("refund_refusal_reason", th.StringType),
                    th.Property(
                        "seller_info",
                        th.ObjectType(
                            th.Property("name", th.StringType),
                            th.Property("store_name", th.StringType),
                            th.Property("store_physical_address", th.StringType),
                            th.Property("store_url", th.StringType),
                        ),
                    ),
                    th.Property("stage", th.StringType),
                    th.Property(
                        "supporting_documents",
                        th.ObjectType(
                            th.Property(
                                "customer_communication_documents",
                                th.ArrayType(th.StringType),
                            ),
                            th.Property(
                                "customer_signature_documents",
                                th.ArrayType(th.StringType),
                            ),
                            th.Property(
                                "documents",
                                th.ArrayType(
                                    th.ObjectType(
                                        th.Property("description", th.StringType),
                                        th.Property(
                                            "file_ids",
                                            th.ArrayType(th.StringType),
                                        ),
                                        th.Property("type", th.StringType),
                                    )
                                ),
                            ),
                            th.Property(
                                "duplicate_charge_defense_documents",
                                th.ArrayType(th.StringType),
                            ),
                            th.Property(
                                "generated_files",
                                th.ArrayType(th.StringType),
                            ),
                            th.Property(
                                "other_documents",
                                th.ArrayType(th.StringType),
                            ),
                            th.Property(
                                "proof_of_delivery_documents",
                                th.ArrayType(th.StringType),
                            ),
                            th.Property(
                                "receipt_documents",
                                th.ArrayType(th.StringType),
                            ),
                            th.Property(
                                "refund_policy_documents",
                                th.ArrayType(th.StringType),
                            ),
                        ),
                    ),
                )
            ),
        ),
        th.Property("created_at", th.DateTimeType),
        th.Property("currency", th.StringType),
        th.Property("customer_id", th.StringType),
        th.Property("customer_name", th.StringType),
        th.Property("due_at", th.DateTimeType),
        th.Property("id", th.StringType),
        th.Property("issuer_comment", th.StringType),
        th.Property("issuer_documents", th.ArrayType(th.StringType)),
        th.Property("merchant_order_id", th.StringType),
        th.Property(
            "metadata",
            th.CustomType({"type": ["object", "string"]}),
        ),
        th.Property("mode", th.StringType),
        th.Property("payment_attempt_id", th.StringType),
        th.Property("payment_intent_id", th.StringType),
        th.Property("payment_method_type", th.StringType),
        th.Property(
            "reason",
            th.ObjectType(
                th.Property("description", th.StringType),
                th.Property("original_code", th.StringType),
                th.Property("type", th.StringType),
            ),
        ),
        th.Property(
            "refunds",
            th.ArrayType(
                th.ObjectType(
                    th.Property("acquirer_reference_number", th.StringType),
                    th.Property("id", th.StringType),
                )
            ),
        ),
        th.Property("stage", th.StringType),
        th.Property("status", th.StringType),
        th.Property("transaction_type", th.StringType),
        th.Property("updated_at", th.DateTimeType),
    ).to_dict()

    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any]
    ) -> Optional[Any]:
        """Return a token for identifying next page or None if no more pages."""
        return response.json().get("page_after")


class PaymentAttemptsStream(AirwallexStream):
    """Define payment attempts stream."""

    name = "payment_attempts"
    path = "/pa/payment_attempts"
    primary_keys = ["id"]
    permission_type = "account"
    replication_key_filter_field = "from_created_at"
    replication_key = "created_at"
    parent_stream_type = AccountDetailsStream

    schema = th.PropertiesList(
        th.Property("acquirer_reference_number", th.StringType),
        th.Property("amount", th.NumberType),
        th.Property(
            "authentication_data",
            th.ObjectType(
                th.Property("authentication_type", th.StringType),
                th.Property("avs_result", th.StringType),
                th.Property("cvc_code", th.StringType),
                th.Property("cvc_result", th.StringType),
                th.Property(
                    "ds_data",
                    th.CustomType({"type": ["object", "string"]}),
                ),
                th.Property(
                    "fraud_data",
                    th.ObjectType(
                        th.Property("action", th.StringType),
                        th.Property(
                            "post_authorization_check",
                            th.ObjectType(
                                th.Property("action", th.StringType),
                                th.Property(
                                    "risk_factors",
                                    th.ArrayType(
                                        th.ObjectType(
                                            th.Property("description", th.StringType),
                                        )
                                    ),
                                ),
                            ),
                        ),
                        th.Property(
                            "risk_factors",
                            th.ArrayType(
                                th.ObjectType(
                                    th.Property("description", th.StringType),
                                )
                            ),
                        ),
                        th.Property("score", th.StringType),
                    ),
                ),
                th.Property("passkey_setup_status", th.StringType),
                th.Property(
                    "sca_exemption",
                    th.ObjectType(
                        th.Property("applied_exemption", th.StringType),
                        th.Property("requested_exemption", th.StringType),
                    ),
                ),
            ),
        ),
        th.Property("authorization_code", th.StringType),
        th.Property("captured_amount", th.NumberType),
        th.Property("created_at", th.DateTimeType),
        th.Property("currency", th.StringType),
        th.Property(
            "dcc_data",
            th.ObjectType(
                th.Property("amount", th.NumberType),
                th.Property("currency", th.StringType),
            ),
        ),
        th.Property("failure_code", th.StringType),
        th.Property(
            "failure_details",
            th.CustomType({"type": ["object", "string"]}),
        ),
        th.Property("id", th.StringType),
        th.Property("merchant_advice_code", th.StringType),
        th.Property("merchant_order_id", th.StringType),
        th.Property("payment_consent_id", th.StringType),
        th.Property("payment_intent_id", th.StringType),
        th.Property(
            "payment_method",
            th.ObjectType(
                th.Property("created_at", th.DateTimeType),
                th.Property("customer_id", th.StringType),
                th.Property("id", th.StringType),
                th.Property("status", th.StringType),
                th.Property("type", th.StringType),
                th.Property("updated_at", th.DateTimeType),
                th.Property(
                    "card",
                    th.ObjectType(
                        th.Property(
                            "billing",
                            th.ObjectType(
                                th.Property(
                                    "address",
                                    th.ObjectType(
                                        th.Property("city", th.StringType),
                                        th.Property("country_code", th.StringType),
                                        th.Property("postcode", th.StringType),
                                        th.Property("state", th.StringType),
                                        th.Property("street", th.StringType),
                                    ),
                                ),
                                th.Property("email", th.StringType),
                                th.Property("first_name", th.StringType),
                                th.Property("last_name", th.StringType),
                                th.Property("phone_number", th.StringType),
                            ),
                        ),
                        th.Property("bin", th.StringType),
                        th.Property("brand", th.StringType),
                        th.Property(
                            "card_updater_info",
                            th.ObjectType(
                                th.Property("expiry_updated", th.BooleanType),
                                th.Property("number_updated", th.BooleanType),
                            ),
                        ),
                        th.Property("card_type", th.StringType),
                        th.Property("expiry_month", th.StringType),
                        th.Property("expiry_year", th.StringType),
                        th.Property("fingerprint", th.StringType),
                        th.Property("is_commercial", th.BooleanType),
                        th.Property("issuer_country_code", th.StringType),
                        th.Property("issuer_name", th.StringType),
                        th.Property("last4", th.StringType),
                        th.Property("name", th.StringType),
                        th.Property("number_type", th.StringType),
                    ),
                ),
            ),
        ),
        th.Property(
            "payment_method_options",
            th.ObjectType(
                th.Property(
                    "card",
                    th.ObjectType(
                        th.Property("authorization_type", th.StringType),
                    ),
                ),
            ),
        ),
        th.Property("payment_method_transaction_id", th.StringType),
        th.Property("provider_original_response_code", th.StringType),
        th.Property("provider_transaction_id", th.StringType),
        th.Property("refunded_amount", th.NumberType),
        th.Property("settle_via", th.StringType),
        th.Property("status", th.StringType),
        th.Property("updated_at", th.DateTimeType),
    ).to_dict()

