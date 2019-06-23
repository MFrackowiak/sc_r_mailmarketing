from dataclasses import asdict

from aiopg import Pool


async def acquire_cursor(pool: Pool):
    async with pool.acquire() as connection:
        async with connection.cursor() as cursor:
            yield cursor


def asdict_no_id(obj):
    initial_dict = asdict(obj)
    return {key: value for key, value in initial_dict.items() if key != "id"}
