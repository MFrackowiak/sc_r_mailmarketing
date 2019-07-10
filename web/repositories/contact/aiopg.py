from typing import List, Tuple, Dict, Optional

from aiopg.sa import Engine
from sqlalchemy import select, join, and_, func

from web.repositories.contact.abstract import AbstractContactRepository
from web.repositories.sqlalchemy.tables import (
    contact_table,
    segment_table,
    segment_contact_table,
)


class SimplePostgresContactRepository(AbstractContactRepository):
    def __init__(self, db_engine: Engine):
        self._db_engine = db_engine

    async def create_contact(self, contact: Dict):
        async with self._db_engine.acquire() as conn:
            result = await conn.execute(contact_table.insert().values(contact))
            contact["id"] = await result.scalar()
            return contact

    async def get_contact_with_segments(
        self, contact_id: int
    ) -> Tuple[Dict, List[Dict]]:
        async with self._db_engine.acquire() as conn:
            contact_result = await conn.execute(
                contact_table.select(contact_table.c.id == contact_id)
            )
            contact = dict(await contact_result.fetchone())
            segments = await conn.execute(
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

            return contact, list(map(dict, await segments.fetchall()))

    async def read_contacts(self, page: int = 0, per_page: int = 50) -> List[Dict]:
        async with self._db_engine.acquire() as conn:
            contacts = await conn.execute(
                contact_table.select()
                .offset(per_page * page)
                .limit(per_page)
                .order_by(contact_table.c.id)
            )
            return [dict(contact) for contact in await contacts.fetchall()]

    async def update_contact(self, contact: Dict):
        async with self._db_engine.acquire() as conn:
            update = (
                contact_table.update()
                .where(contact_table.c.id == contact["id"])
                .values({key: value for key, value in contact.items() if key != "id"})
            )
            await conn.execute(update)

    async def delete_contact(self, contact_id: int):
        async with self._db_engine.acquire() as conn:
            await conn.execute(
                contact_table.delete().where(contact_table.c.id == contact_id)
            )

    async def create_segment(self, segment: Dict) -> Dict:
        async with self._db_engine.acquire() as conn:
            result = await conn.execute(segment_table.insert().values(segment))
            segment["id"] = await result.scalar()
        return segment

    async def get_segment(self, segment_id: int) -> Dict:
        async with self._db_engine.acquire() as conn:
            segment = await conn.execute(
                segment_table.select(segment_table.c.id == segment_id)
            )
            return dict(await segment.fetchone())

    async def read_segments(self, page: int, per_page: Optional[int]) -> List[Dict]:
        async with self._db_engine.acquire() as conn:
            query = segment_table.select()

            if per_page is not None:
                query = query.offset(per_page * page).limit(per_page)

            segments = await conn.execute(query)
            return [dict(segment) for segment in await segments.fetchall()]

    async def update_segment(self, segment: Dict):
        async with self._db_engine.acquire() as conn:
            update = (
                segment_table.update()
                .where(segment_table.c.id == segment["id"])
                .values({key: value for key, value in segment.items() if key != "id"})
            )
            await conn.execute(update)

    async def delete_segment(self, segment_id: int):
        async with self._db_engine.acquire() as conn:
            await conn.execute(
                segment_table.delete().where(segment_table.c.id == segment_id)
            )

    async def list_contacts_in_segment(self, segment_id: int):
        async with self._db_engine.acquire() as conn:
            query = (
                select(
                    [contact_table.c.id, contact_table.c.name, contact_table.c.email],
                    segment_contact_table.c.segment_id == segment_id,
                )
                .select_from(
                    join(
                        contact_table,
                        segment_contact_table,
                        contact_table.c.id == segment_contact_table.c.contact_id,
                    )
                )
                .order_by(contact_table.c.id)
            )

            contacts = await conn.execute(query)
            return list(map(dict, await contacts.fetchall()))

    async def add_contact_to_segment(self, segment_id: int, contact_id: int):
        async with self._db_engine.acquire() as conn:
            await conn.execute(
                segment_contact_table.insert().values(
                    {"segment_id": segment_id, "contact_id": contact_id}
                )
            )

    async def remove_contact_from_segment(self, segment_id: int, contact_id: int):
        async with self._db_engine.acquire() as conn:
            await conn.execute(
                segment_contact_table.delete().where(
                    and_(
                        segment_contact_table.c.segment_id == segment_id,
                        segment_contact_table.c.contact_id == contact_id,
                    )
                )
            )

    async def get_contacts_count(self) -> int:
        async with self._db_engine.acquire() as conn:
            result = await conn.execute(
                select([func.count()]).select_from(contact_table)
            )
            return await result.scalar()

    async def get_segments_count(self) -> int:
        async with self._db_engine.acquire() as conn:
            result = await conn.execute(
                select([func.count()]).select_from(segment_table)
            )
            return await result.scalar()
