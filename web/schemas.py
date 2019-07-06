from voluptuous import Schema, Email, Coerce, And

from web.validation import validate_template_schema

contact_schema = Schema(
    {"name": str, "email": Email(), "first_name": str, "last_name": str}, required=True
)


segment_schema = Schema({"name": str}, required=True)


template_schema = And(
    Schema({"name": str, "template": str}, required=True), validate_template_schema
)


segment_contact_join_schema = Schema({"segment_id": Coerce(int)}, required=True)
