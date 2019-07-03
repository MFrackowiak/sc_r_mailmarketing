from sqlalchemy import MetaData, Table, Column, Integer, String, Text

metadata = MetaData()

contact_table = Table(
    "contact",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(64)),
    Column("email", String(128), unique=True),
    Column("first_name", String(64), default=""),
    Column("last_name", String(64), default=""),
)

segment_table = Table(
    "segment",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(64), unique=True),
)


segment_contact_table = Table(
    "segment_contact",
    metadata,
    Column("contact_id", Integer),
    Column("segment_id", Integer),
)


email_template_table = Table(
    "email_template",
    metadata,
    Column("id", Integer),
    Column("name", String(128)),
    Column("template", Text),
)


email_request_table = Table(
    "email_request",
    metadata,
    Column("id", Integer),
    Column("name", String(128)),
    Column("template_id", Integer),
    Column("segment_id", Integer),
)


job_table = Table(
    "job",
    metadata,
    Column("id", Integer),
    Column("request_id", Integer),
    Column("status", String(16)),
    Column("contact_id", Integer),
)
