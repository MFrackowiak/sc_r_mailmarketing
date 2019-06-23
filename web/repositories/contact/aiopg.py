from typing import List, Tuple, Dict

from aiopg.sa import Engine
from sqlalchemy import select, join

from web.repositories.contact.abstract import AbstractContactRepository
from web.repositories.sqlalchemy.tables import (
    contact_table,
    segment_table,
    segment_contact_table,
)
from web.repositories.utils import asdict_no_id


class SimplePostgresContactRepository(AbstractContactRepository):
    def __init__(self, db_engine: Engine):
        self._db_engine = db_engine

    async def create_contact(self, contact: Dict):
        async with self._db_engine.acquire() as conn:
            await conn.execute(contact_table.insert().values(asdict_no_id(contact)))
            contact.contact_id = conn.inserted_primary_key[0]

    async def get_contact_with_segments(
        self, contact_id: int
    ) -> Tuple[Dict, List[Dict]]:
        async with self._db_engine.acquire() as conn:
            contact = await conn.fetchone(
                contact_table.select(contact_table.c.id == contact_id)
            )
            segments = await conn.fetchall(
                select(
                    [segment_table.c.id, segment_table.c.name],
                    segment_contact_table.c.contact_id == contact_id,
                ).select_from(
                    join(
                        segment_table,
                        segment_contact_table,
                        segment_table.c.id == segment_contact_table.c.segment_id,
                    )
                )
            )

        return (
            dict(contact),
            [{"id": seg_id, "name": seg_name} for seg_id, seg_name in segments],
        )

    async def read_contacts(self, page: int, per_page: int) -> List[Dict]:
        async with self._db_engine.acquire() as conn:
            contacts = await conn.fetchall(
                contact_table.select().offset(per_page * page).limit(per_page)
            )
        return [dict(contact) for contact in contacts]

    async def update_contact(self, contact: Dict):
        pass

    async def delete_contact(self, contact_id: int):
        pass

    async def create_segment(self, segment: Dict):
        pass

    async def get_segment(self, segment_id: int) -> Dict:
        pass

    async def read_segments(self, page: int, per_page: int) -> List[Dict]:
        pass

    async def update_segment(self, segment: Dict):
        pass

    async def delete_segment(self, segment_id: int):
        pass

    async def list_contacts_in_segment(self, segment_id: int):
        pass

    async def add_contact_to_segment(self, segment_id: int, contact_id: int):
        pass

    async def remove_contact_from_segment(self, segment_id: int, contact_id: int):
        pass
