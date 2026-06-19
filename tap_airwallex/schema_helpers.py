import hotglue_singer_sdk.typing as th

_account_amount_currency_type = th.ObjectType(
    th.Property("amount", th.StringType),
    th.Property("currency", th.StringType),
)

_account_address_simple_type = th.ObjectType(
    th.Property("country_code", th.StringType),
    th.Property("postcode", th.StringType),
)

_account_address_full_type = th.ObjectType(
    th.Property("address_line1", th.StringType),
    th.Property("country_code", th.StringType),
    th.Property("postcode", th.StringType),
    th.Property("state", th.StringType),
    th.Property("suburb", th.StringType),
)

_account_business_identifier_type = th.ObjectType(
    th.Property("country_code", th.StringType),
    th.Property("number", th.StringType),
    th.Property("type", th.StringType),
)

_account_business_usage_type = th.ObjectType(
    th.Property("estimated_monthly_revenue", _account_amount_currency_type),
    th.Property("product_reference", th.ArrayType(th.StringType)),
)

_account_business_details_attachments_type = th.ObjectType(
    th.Property("business_documents", th.ArrayType(th.ObjectType())),
)

_account_business_details_type = th.ObjectType(
    th.Property("account_usage", _account_business_usage_type),
    th.Property("as_trustee", th.StringType),
    th.Property("attachments", _account_business_details_attachments_type),
    th.Property("business_address", _account_address_simple_type),
    th.Property(
        "business_identifiers",
        th.ArrayType(_account_business_identifier_type),
    ),
    th.Property("business_name", th.StringType),
    th.Property("business_name_english", th.StringType),
    th.Property("business_name_trading", th.StringType),
    th.Property("business_start_date", th.StringType),
    th.Property("business_structure", th.StringType),
    th.Property("contact_number", th.StringType),
    th.Property("description_of_goods_or_services", th.StringType),
    th.Property("explanation_for_high_risk_countries_exposure", th.StringType),
    th.Property("exports_goods_or_services", th.BooleanType),
    th.Property("has_member_holding_public_office", th.BooleanType),
    th.Property("has_nominee_shareholders", th.BooleanType),
    th.Property("has_prior_financial_institution_refusal", th.BooleanType),
    th.Property("has_ringgit_borrowing", th.BooleanType),
    th.Property("industry_category_code", th.StringType),
    th.Property("no_shareholders_with_over_25percent", th.BooleanType),
    th.Property("operating_country", th.ArrayType(th.StringType)),
    th.Property("registration_address", _account_address_simple_type),
    th.Property("registration_address_english", _account_address_full_type),
    th.Property("state_of_incorporation", th.StringType),
    th.Property("url", th.StringType),
    th.Property("urls", th.ArrayType(th.StringType)),
)

_account_tax_id_type = th.ObjectType(
    th.Property("number", th.StringType),
    th.Property("type", th.StringType),
)

_account_identification_primary_type = th.ObjectType(
    th.Property("identification_type", th.StringType),
    th.Property("issuing_country_code", th.StringType),
    th.Property("tax_id", _account_tax_id_type),
)

_account_identifications_type = th.ObjectType(
    th.Property("primary", _account_identification_primary_type),
)

_account_business_person_attachments_type = th.ObjectType(
    th.Property("business_person_documents", th.ArrayType(th.ObjectType())),
)

_account_business_person_type = th.ObjectType(
    th.Property("attachments", _account_business_person_attachments_type),
    th.Property("date_of_birth", th.StringType),
    th.Property("email", th.StringType),
    th.Property("first_name_english", th.StringType),
    th.Property("identifications", _account_identifications_type),
    th.Property("job_title", th.StringType),
    th.Property("last_name_english", th.StringType),
    th.Property("nationality", th.StringType),
    th.Property("person_id", th.StringType),
    th.Property("phone_number", th.StringType),
    th.Property("residential_address", _account_address_simple_type),
    th.Property("roles", th.ArrayType(th.StringType)),
)

_account_payment_distribution_type = th.ObjectType(
    th.Property("payment_type", th.StringType),
    th.Property("percentage", th.StringType),
)

_account_store_website_type = th.ObjectType(
    th.Property("url", th.StringType),
)

_account_estimated_transaction_volume_type = th.ObjectType(
    th.Property("average_amount_per_transaction", th.StringType),
    th.Property("currency", th.StringType),
    th.Property("max_amount_per_transaction", th.StringType),
    th.Property("monthly_transaction_amount", th.StringType),
)

_account_store_details_type = th.ObjectType(
    th.Property("cross_border_transaction_percent", th.StringType),
    th.Property("employee_size", th.IntegerType),
    th.Property(
        "estimated_transaction_volume",
        _account_estimated_transaction_volume_type,
    ),
    th.Property("financial_statements", th.ArrayType(th.ObjectType())),
    th.Property("fulfillment_days", th.IntegerType),
    th.Property("industry_code", th.StringType),
    th.Property("mcc", th.StringType),
    th.Property("operating_models", th.ArrayType(th.StringType)),
    th.Property(
        "payment_distribution",
        th.ArrayType(_account_payment_distribution_type),
    ),
    th.Property("selling_to_country_codes", th.ArrayType(th.StringType)),
    th.Property("shipping_from_country_codes", th.ArrayType(th.StringType)),
    th.Property("store_description", th.StringType),
    th.Property("store_name", th.StringType),
    th.Property("store_photos", th.ArrayType(th.ObjectType())),
    th.Property("store_websites", th.ArrayType(_account_store_website_type)),
)

_account_details_attachments_type = th.ObjectType(
    th.Property("additional_files", th.ArrayType(th.ObjectType())),
)

_account_details_type = th.ObjectType(
    th.Property("attachments", _account_details_attachments_type),
    th.Property("business_details", _account_business_details_type),
    th.Property(
        "business_person_details",
        th.ArrayType(_account_business_person_type),
    ),
    th.Property("store_details", _account_store_details_type),
    th.Property("trustee_details", th.ObjectType()),
    th.Property("individual_details", th.ObjectType()),
    th.Property("legal_entity_id", th.StringType),
    th.Property("legal_entity_identifier", th.StringType),
    th.Property("legal_entity_type", th.StringType),
)

_account_customer_agreements_terms_type = th.ObjectType(
    th.Property("device_data", th.ObjectType()),
    th.Property("service_agreement_type", th.StringType),
)

_account_customer_agreements_type = th.ObjectType(
    th.Property("agreed_to_data_usage", th.BooleanType),
    th.Property("agreed_to_terms_and_conditions", th.BooleanType),
    th.Property("opt_in_for_marketing", th.BooleanType),
    th.Property("terms_and_conditions", _account_customer_agreements_terms_type),
)

_account_primary_contact_attachments_type = th.ObjectType(
    th.Property("identity_files", th.ArrayType(th.ObjectType())),
)

_account_primary_contact_type = th.ObjectType(
    th.Property("attachments", _account_primary_contact_attachments_type),
    th.Property("email", th.StringType),
    th.Property("mobile", th.StringType),
)

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

_transfer_address_type = th.ObjectType(
    th.Property("city", th.StringType),
    th.Property("country_code", th.StringType),
    th.Property("postcode", th.StringType),
    th.Property("state", th.StringType),
    th.Property("street_address", th.StringType),
)

_transfer_beneficiary_additional_info_type = th.ObjectType(
    th.Property("personal_id_number", th.StringType),
    th.Property("personal_id_type", th.StringType),
    th.Property("personal_mobile_number", th.StringType),
)

_transfer_beneficiary_bank_details_type = th.ObjectType(
    th.Property("account_currency", th.StringType),
    th.Property("account_name", th.StringType),
    th.Property("account_number", th.StringType),
    th.Property("bank_country_code", th.StringType),
    th.Property("bank_name", th.StringType),
    th.Property("swift_code", th.StringType),
)

_transfer_beneficiary_type = th.ObjectType(
    th.Property("additional_info", _transfer_beneficiary_additional_info_type),
    th.Property("address", _transfer_address_type),
    th.Property("bank_details", _transfer_beneficiary_bank_details_type),
    th.Property("date_of_birth", th.StringType),
    th.Property("entity_type", th.StringType),
    th.Property("first_name", th.StringType),
    th.Property("last_name", th.StringType),
    th.Property("type", th.StringType),
)

_transfer_conversion_type = th.ObjectType(
    th.Property("currency_pair", th.StringType),
    th.Property("rate", th.NumberType),
)

_transfer_funding_type = th.ObjectType(
    th.Property("status", th.StringType),
)

_transfer_payer_additional_info_type = th.ObjectType(
    th.Property("business_incorporation_date", th.StringType),
    th.Property("business_registration_number", th.StringType),
    th.Property("business_registration_type", th.StringType),
)

_transfer_payer_type = th.ObjectType(
    th.Property("additional_info", _transfer_payer_additional_info_type),
    th.Property("address", _transfer_address_type),
    th.Property("company_name", th.StringType),
    th.Property("entity_type", th.StringType),
)

