from voluptuous import Or, Schema, Email, Optional, ALLOW_EXTRA, Length, And


job_schema = Schema(
    {"id": Or(str, int), "email": Email(), Optional("name"): str},
    required=True,
    extra=ALLOW_EXTRA,
)

job_request_schema = Schema(
    {"jobs": And([job_schema], Length(min=1)), "template": str, "subject": str},
    required=True,
)

settings_schema = Schema(
    {
        "auth": {"user": str, "password": str},
        "email_from": {"name": str, "email": Email()},
        "headers": dict,
    }
)
