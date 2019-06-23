from sqlalchemy import MetaData, Table, Column, Integer, String

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
