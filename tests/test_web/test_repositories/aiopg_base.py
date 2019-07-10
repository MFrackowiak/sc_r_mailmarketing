import traceback
from asyncio import get_event_loop, sleep

from asynctest import TestCase, logging, SkipTest

from web.app import init_db
from web.repositories.contact.aiopg import SimplePostgresContactRepository


class DBEngineMock:
    def __init__(self, connection):
        self.conn = connection
        self.acquired = False

    async def __aenter__(self):
        return self.conn

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await sleep(0.1)

    def acquire(self):
        self.acquired = True
        return self

    def assert_was_acquired(self):
        assert self.acquired


class AioPGBaseTestCase(TestCase):
    loop = get_event_loop()
    use_default_loop = True

    @classmethod
    def setUpClass(cls):
        try:
            cls.engine = cls.loop.run_until_complete(
                init_db("config/database-test.json", force_init_db=True)
            )
        except Exception:
            logging.error(
                f"Could not set up database, aborting aiopg tests. Error: {traceback.format_exc()}"
            )
            cls.engine = None
            cls.connection = None
        else:
            cls.connection = cls.loop.run_until_complete(cls.engine.acquire())
            super().setUpClass()

    async def setUp(self):
        if not self.engine:
            raise SkipTest("PostgresDB not available or configured.")
        self.transaction = await self.connection.begin()

        self.db_engine_mock = DBEngineMock(self.connection)
        self.repository = SimplePostgresContactRepository(self.db_engine_mock)

    async def tearDown(self):
        await self.transaction.rollback()

    @classmethod
    def tearDownClass(cls):
        if cls.connection:
            cls.connection.close()
            cls.engine.close()
        super().tearDownClass()
