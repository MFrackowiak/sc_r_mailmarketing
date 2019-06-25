from json import load

from aiopg.sa import create_engine


async def init_db(config_file: str):
    with open(config_file) as dbconfig:
        config = load(dbconfig)

    engine = await create_engine(
        user=config["user"],
        database=config["name"],
        host=config["host"],
        password=config["password"],
    )

    with open(config["sql"]) as sql_file:
        init_sql = sql_file.read()

    async with engine.acquire() as conn:
        await conn.execute(init_sql)

    return engine
