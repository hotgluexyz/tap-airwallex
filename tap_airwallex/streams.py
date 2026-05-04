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


_bill_card_transaction_type = th.ObjectType(
    th.Property("account_id", th.StringType),
    th.Property("card_funding_type", th.StringType),
    th.Property("card_id", th.StringType),
    th.Property("card_transaction_id", th.StringType),
    th.Property("source_amount", th.StringType),
    th.Property("source_currency", th.StringType),
    th.Property("transacted_at", th.DateTimeType),
)

_bill_transfer_type = th.ObjectType(
    th.Property("account_id", th.StringType),
    th.Property("multi_bill", th.BooleanType),
    th.Property("source_amount", th.StringType),
    th.Property("source_currency", th.StringType),
    th.Property("transfer_date", th.DateTimeType),
    th.Property("transfer_id", th.StringType),
)

_bill_payment_type = th.ObjectType(
    th.Property("amount", th.StringType),
    th.Property("card_transaction", _bill_card_transaction_type),
    th.Property("created_at", th.DateTimeType),
    th.Property("currency", th.StringType),
    th.Property("id", th.StringType),
    th.Property("transfer", _bill_transfer_type),
    th.Property("type", th.StringType),
)

_bill_attachment_type = th.ObjectType(
    th.Property("content_type", th.StringType),
    th.Property("created_at", th.DateTimeType),
    th.Property("file_name", th.StringType),
    th.Property("file_url", th.StringType),
    th.Property("id", th.StringType),
)

_bill_accounting_field_selection_type = th.ObjectType(
    th.Property("external_id", th.StringType),
    th.Property("name", th.StringType),
    th.Property("type", th.StringType),
    th.Property("value", th.StringType),
    th.Property("value_label", th.StringType),
)

_bill_line_item_type = th.ObjectType(
    th.Property(
        "accounting_field_selections",
        th.ArrayType(_bill_accounting_field_selection_type),
    ),
    th.Property("description", th.StringType),
    th.Property("id", th.StringType),
    th.Property("purchase_order_line_item_id", th.StringType),
    th.Property("quantity", th.StringType),
    th.Property("tax_amount", th.StringType),
    th.Property("total_amount", th.StringType),
    th.Property("unit_price", th.StringType),
)


class BillsStream(AirwallexStream):
    """Define custom stream."""

    name = "bills"
    path = "/spend/bills"
    primary_keys = ["id"]
    replication_key = "created_at"
    replication_key_filter_field = "from_created_at"
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
