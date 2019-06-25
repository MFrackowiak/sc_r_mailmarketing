from asyncio import get_event_loop

from asynctest import TestCase
from sqlalchemy.engine import reflection

from web.app import init_db
from web.repositories.contact.aiopg import SimplePostgresContactRepository
from web.repositories.sqlalchemy.tables import contact_table


class DBEngineMock:
    def __init__(self, connection):
        self.conn = connection
        self.acquired = False

    async def __aenter__(self):
        return self.conn

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    def acquire(self):
        self.acquired = True
        return self

    def assert_was_acquired(self):
        assert self.acquired


class AioPGContactRepositoryTestCase(TestCase):
    loop = get_event_loop()
    use_default_loop = True

    @classmethod
    def setUpClass(cls):
        cls.engine = cls.loop.run_until_complete(init_db("../database-test.json"))

        super().setUpClass()

    async def setUp(self):
        self.connection = await self.engine.acquire()
        self.transaction = await self.connection.begin()

        self.db_engine_mock = DBEngineMock(self.connection)
        self.repository = SimplePostgresContactRepository(self.db_engine_mock)

    async def tearDown(self):
        await self.transaction.rollback()
        self.connection.close()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        cls.engine.close()

    async def test_create_contact(self):
        contact = await self.repository.create_contact(
            {
                "name": "User1",
                "first_name": "Janusz",
                "last_name": "Kowalski",
                "email": "jk@co.co",
            }
        )

        self.assertIn("id", contact)
        self.assertEqual(
            contact,
            {
                "name": "User1",
                "first_name": "Janusz",
                "last_name": "Kowalski",
                "email": "jk@co.co",
                "id": 1,
            },
        )
        self.db_engine_mock.assert_was_acquired()
