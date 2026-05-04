from hotglue_singer_sdk import typing as th

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
