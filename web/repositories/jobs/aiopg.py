from typing import Dict, List

from aiopg.sa import Engine
from sqlalchemy import select, join, insert

from common.enums import EmailResult
from web.repositories.jobs.abstract import AbstractJobRepository
from web.repositories.sqlalchemy.tables import (
    email_request_table,
    job_table,
    segment_contact_table,
    contact_table,
)


class SimplePostgresJobRepository(AbstractJobRepository):
    def __init__(self, db_engine: Engine):
        self._db_engine = db_engine

    async def create_email_request(self, segment_id: int, template_id: int, name: str):
        async with self._db_engine.acquire() as conn:
            # async with conn.begin():
            result = await conn.execute(
                email_request_table.insert().values(
                    {"name": name, "template_id": template_id, "segment_id": segment_id}
                )
            )
            request_id = 1  # await result.scalar()

            await conn.execute(
                job_table.insert(
                    [
                        segment_contact_table.c.request_id,
                        segment_contact_table.c.status,
                        segment_contact_table.c.contact_id,
                    ]
                ).from_select(
                    [
                        request_id,
                        EmailResult.PENDING.value,
                        segment_contact_table.c.contact_id,
                    ],
                    segment_contact_table.select().where(
                        segment_contact_table.c.segment_id == segment_id
                    ),
                )
            )
        return {
            "segment_id": segment_id,
            "template_id": template_id,
            "id": request_id,
            "name": name,
        }

    async def get_email_request_job_data(self, email_request_id: int) -> List[Dict]:
        async with self._db_engine.acquire() as conn:
            results = await conn.execute(
                select(
                    [
                        contact_table.c.id,
                        contact_table.c.name,
                        contact_table.c.email,
                        contact_table.c.first_name,
                        contact_table.c.last_name,
                    ],
                    job_table.c.request_id == email_request_id,
                ).select_from(
                    join(
                        contact_table,
                        job_table,
                        job_table.c.contact_id == contact_table.c.id,
                    )
                )
            )

            return [dict(job) for job in await results.fetchall()]

    async def get_email_requests(self) -> List[Dict]:
        pass

    async def get_email_request(self, request_id: int) -> Dict:
        pass

    async def get_email_requests_job_statuses(
        self, email_request_id: int
    ) -> List[Dict]:
        pass

    async def update_job_statuses(self, statuses: Dict):
        pass
