from typing import Dict, List

from aiopg.sa import Engine
from aiopg.sa.result import RowProxy
from sqlalchemy import select, join, literal, case

from common.enums import EmailResult
from web.repositories.jobs.abstract import AbstractJobRepository
from web.repositories.sqlalchemy.tables import (
    email_request_table,
    job_table,
    segment_contact_table,
    contact_table,
    email_template_table,
    segment_table,
)


class SimplePostgresJobRepository(AbstractJobRepository):
    def __init__(self, db_engine: Engine):
        self._db_engine = db_engine

    async def create_email_request(self, segment_id: int, template_id: int, name: str):
        async with self._db_engine.acquire() as conn:
            async with conn.begin():
                result = await conn.execute(
                    email_request_table.insert()
                    .values(
                        {
                            "name": name,
                            "template_id": template_id,
                            "segment_id": segment_id,
                        }
                    )
                    .returning(email_request_table.c.id)
                )
                request_id = await result.scalar()

                await conn.execute(
                    job_table.insert().from_select(
                        [
                            job_table.c.request_id,
                            job_table.c.status,
                            job_table.c.contact_id,
                        ],
                        select(
                            [
                                literal(request_id),
                                literal(EmailResult.PENDING.value),
                                segment_contact_table.c.contact_id,
                            ],
                            segment_contact_table.c.segment_id == segment_id,
                            segment_contact_table,
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
                        job_table.c.id,
                    ],
                    job_table.c.request_id == email_request_id,
                    use_labels=True,
                )
                .select_from(
                    join(
                        contact_table,
                        job_table,
                        job_table.c.contact_id == contact_table.c.id,
                    )
                )
                .order_by(job_table.c.id)
            )

            return [
                {
                    "id": jid,
                    "name": name,
                    "user_id": uid,
                    "first_name": fname,
                    "last_name": lname,
                    "email": email,
                }
                for uid, name, email, fname, lname, jid in map(
                    RowProxy.as_tuple, await results.fetchall()
                )
            ]

    async def get_email_requests(self) -> List[Dict]:
        async with self._db_engine.acquire() as conn:
            requests = await conn.execute(
                select([email_request_table.c.id, email_request_table.c.name])
                .select_from(email_request_table)
                .order_by(email_request_table.c.id)
            )
            return [dict(request) for request in await requests.fetchall()]

    async def get_email_request(self, request_id: int) -> Dict:
        async with self._db_engine.acquire() as conn:
            requests = await conn.execute(
                select(
                    [
                        email_request_table.c.id,
                        email_request_table.c.name,
                        email_request_table.c.template_id,
                        email_template_table.c.name,
                        email_request_table.c.segment_id,
                        segment_table.c.name,
                    ],
                    email_request_table.c.id == request_id,
                    use_labels=True,
                )
                .select_from(
                    join(
                        join(
                            email_request_table,
                            email_template_table,
                            email_template_table.c.id
                            == email_request_table.c.template_id,
                        ),
                        segment_table,
                        email_request_table.c.segment_id == segment_table.c.id,
                    )
                )
                .order_by(email_request_table.c.id)
            )
            rid, rname, tid, tname, sid, sname = (await requests.fetchone()).as_tuple()
            return {
                "id": rid,
                "name": rname,
                "template": {"name": tname, "id": tid},
                "segment": {"name": sname, "id": sid},
            }

    async def get_email_requests_job_statuses(
        self, email_request_id: int
    ) -> List[Dict]:
        async with self._db_engine.acquire() as conn:
            jobs = await conn.execute(
                select(
                    [
                        job_table.c.id,
                        job_table.c.status,
                        contact_table.c.name,
                        contact_table.c.id,
                    ],
                    job_table.c.request_id == email_request_id,
                    use_labels=True,
                ).select_from(
                    join(
                        job_table,
                        contact_table,
                        job_table.c.contact_id == contact_table.c.id,
                    )
                )
            )
            return [
                {"id": jid, "status": status, "contact": {"name": name, "id": cid}}
                for jid, status, name, cid in map(
                    RowProxy.as_tuple, await jobs.fetchall()
                )
            ]

    async def update_job_statuses(self, statuses: Dict):
        async with self._db_engine.acquire() as conn:
            query = (
                job_table.update()
                .where(job_table.c.id.in_(sum(statuses.values(), [])))
                .values(
                    status=case(
                        [
                            (job_table.c.id.in_(job_ids), status)
                            for status, job_ids in statuses.items()
                        ]
                    )
                )
            )
            await conn.execute(query)
