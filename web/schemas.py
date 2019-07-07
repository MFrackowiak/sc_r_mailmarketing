from voluptuous import Schema, Email, Coerce, Inclusive, In

from common.enums import EmailResult

contact_schema = Schema(
    {"name": str, "email": Email(), "first_name": str, "last_name": str}, required=True
)

segment_schema = Schema({"name": str}, required=True)

template_schema = Schema({"name": str, "template": str}, required=True)

segment_contact_join_schema = Schema({"segment_id": Coerce(int)}, required=True)

settings_schema = Schema(
    {
        Inclusive("name", "from"): str,
        Inclusive("email", "from"): Email(),
        Inclusive("user", "auth"): str,
        Inclusive("password", "auth"): str,
    }
)


campaign_schema = Schema(
    {"segment_id": Coerce(int), "template_id": Coerce(int), "subject": str},
    required=True,
)

update_status_schema = Schema(
    {
        In(frozenset(result.value for result in EmailResult)): [
            {"id": int, "message_id": str}
        ]
    },
    required=True,
)
