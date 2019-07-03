from tests.test_web.test_repositories.aiopg_base import AioPGBaseTestCase
from web.repositories.jobs.aiopg import SimplePostgresJobRepository


class AioPGContactRepositoryTestCase(AioPGBaseTestCase):
    async def setUp(self):
        await super().setUp()
        self.repository = SimplePostgresJobRepository(self.db_engine_mock)

    async def _generate_base_data(self):
        await self.connection.execute(
            """
            INSERT INTO segment (id, name) VALUES (1, 'test-seg')
            """
        )
        await self.connection.execute(
            """
            INSERT INTO contact (id, name, first_name, last_name, email)
            VALUES
            (1, 'User1', 'Janusz', 'Kowalski', 'jk1@co.co'),
            (2, 'User2', 'Janusz', 'Kowalski', 'jk2@co.co'),
            (3, 'User3', 'Janusz', 'Kowalski', 'jk3@co.co'),
            (4, 'User4', 'Janusz', 'Kowalski', 'jk4@co.co')
            """
        )
        await self.connection.execute(
            """
            INSERT INTO segment_contact (contact_id, segment_id)
            VALUES (1, 1), (2, 1), (3, 1), (4, 1)
            """
        )
        await self.connection.execute(
            """
            INSERT INTO email_template (id, name, template) VALUES 
            (1, 'test-template', 'Hello user! We are here to help.')
            """
        )

    async def test_create_email_request(self):
        await self._generate_base_data()

        request = await self.repository.create_email_request(1, 1, "My test campaign")
        self.assertEqual(
            {"id": 1, "segment_id": 1, "template_id": 1, "name": "My test campaign"},
            request,
        )

        stored_request = await self.connection.execute(
            """
            SELECT id, name, template_id, segment_id FROM email_request
            """
        )
        self.assertEqual((1, "My test campaign", 1, 1), await stored_request.fetchone())
        jobs = await self.connection.execute(
            """
            SELECT request_id, status, contact_id FROM job ORDER BY contact_id
            """
        )
        self.assertEqual(
            [
                (1, "PENDING", 1),
                (1, "PENDING", 2),
                (1, "PENDING", 3),
                (1, "PENDING", 4),
            ],
            await jobs.fetchall(),
        )
