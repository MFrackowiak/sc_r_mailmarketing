from common.enums import EmailResult
from tests.test_web.test_repositories.aiopg_base import AioPGBaseTestCase
from web.repositories.jobs.aiopg import SimplePostgresJobRepository


class AioPGContactRepositoryTestCase(AioPGBaseTestCase):
    async def setUp(self):
        await super().setUp()
        self.repository = SimplePostgresJobRepository(self.db_engine_mock)

    async def _generate_base_data(self):
        await self.connection.execute(
            """
            INSERT INTO segment (id, name) VALUES (1, 'test-seg'), (2, 'seg')
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
            VALUES (1, 1), (2, 1), (3, 1), (4, 1), (2, 2), (3, 2)
            """
        )
        await self.connection.execute(
            """
            INSERT INTO email_template (id, name, template) VALUES 
            (1, 'test-template', 'Hello user! We are here to help.'),
            (2, 'template-2', 'Hello user! We are here to profit.')
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
                (1, "pending", 1),
                (1, "pending", 2),
                (1, "pending", 3),
                (1, "pending", 4),
            ],
            await jobs.fetchall(),
        )

    async def test_get_email_request_job_data(self):
        await self._generate_base_data()
        await self.connection.execute(
            """
            INSERT INTO email_request (id, name, template_id, segment_id)
            VALUES (1, 'test-camp', 1, 1)
            """
        )
        await self.connection.execute(
            """
            INSERT INTO job (id, request_id, contact_id, status)
            SELECT contact_id, 1, contact_id, 'pending'
            FROM segment_contact WHERE segment_id = 1
            """
        )

        jobs = await self.repository.get_email_request_job_data(1)

        self.assertEqual(
            [
                {
                    "email": "jk1@co.co",
                    "first_name": "Janusz",
                    "id": 1,
                    "last_name": "Kowalski",
                    "name": "User1",
                    "user_id": 1,
                },
                {
                    "email": "jk2@co.co",
                    "first_name": "Janusz",
                    "id": 2,
                    "last_name": "Kowalski",
                    "name": "User2",
                    "user_id": 2,
                },
                {
                    "email": "jk3@co.co",
                    "first_name": "Janusz",
                    "id": 3,
                    "last_name": "Kowalski",
                    "name": "User3",
                    "user_id": 3,
                },
                {
                    "email": "jk4@co.co",
                    "first_name": "Janusz",
                    "id": 4,
                    "last_name": "Kowalski",
                    "name": "User4",
                    "user_id": 4,
                },
            ],
            jobs,
        )

    async def test_get_email_requests(self):
        await self._generate_base_data()
        await self.connection.execute(
            """
            INSERT INTO email_request (id, name, template_id, segment_id)
            VALUES (1, 'test-camp', 1, 1), (2, 'camp2', 2, 1), (3, 'camp3', 2, 2)
            """
        )

        campaigns = await self.repository.get_email_requests()

        self.assertEqual(
            [
                {"id": 1, "name": "test-camp"},
                {"id": 2, "name": "camp2"},
                {"id": 3, "name": "camp3"},
            ],
            campaigns,
        )

    async def test_get_email_request(self):
        await self._generate_base_data()
        await self.connection.execute(
            """
            INSERT INTO email_request (id, name, template_id, segment_id)
            VALUES (1, 'test-camp', 1, 1), (2, 'camp2', 2, 1), (3, 'camp3', 2, 2)
            """
        )

        campaign = await self.repository.get_email_request(3)

        self.assertEqual(
            {
                "id": 3,
                "name": "camp3",
                "segment": {"name": "seg", "id": 2},
                "template": {"name": "template-2", "id": 2},
            },
            campaign,
        )

    async def test_get_email_request_job_statuses(self):
        await self._generate_base_data()
        await self.connection.execute(
            """
            INSERT INTO email_request (id, name, template_id, segment_id)
            VALUES (1, 'test-camp', 1, 1)
            """
        )
        await self.connection.execute(
            """
            INSERT INTO job (id, request_id, contact_id, status)
            SELECT contact_id, 1, contact_id, 'pending'
            FROM segment_contact WHERE segment_id = 1
            """
        )
        await self.connection.execute(
            "UPDATE job SET status = 'success' WHERE id IN (2, 4)"
        )
        await self.connection.execute("UPDATE job SET status = 'retry' WHERE id = 3")

        jobs = await self.repository.get_email_requests_job_statuses(1)

        self.assertEqual(
            [
                {"id": 1, "status": "pending", "contact": {"name": "User1", "id": 1}},
                {"id": 2, "status": "success", "contact": {"name": "User2", "id": 2}},
                {"id": 3, "status": "retry", "contact": {"name": "User3", "id": 3}},
                {"id": 4, "status": "success", "contact": {"name": "User4", "id": 4}},
            ],
            jobs,
        )

    async def test_update_job_statuses(self):
        await self._generate_base_data()
        await self.connection.execute(
            """
            INSERT INTO email_request (id, name, template_id, segment_id)
            VALUES (1, 'test-camp', 1, 1)
            """
        )
        await self.connection.execute(
            """
            INSERT INTO job (id, request_id, contact_id, status)
            SELECT contact_id, 1, contact_id, 'pending'
            FROM segment_contact WHERE segment_id = 1
            """
        )

        await self.repository.update_job_statuses(
            {
                EmailResult.SUCCESS.value: [1, 2],
                EmailResult.FAILURE.value: [3],
                EmailResult.RECOVERABLE_FAILURE.value: [4],
            }
        )

        post_update = await self.connection.execute("SELECT id, status FROM job")

        self.assertEqual(
            [(1, "success"), (2, "success"), (3, "failure"), (4, "retry")],
            await post_update.fetchall(),
        )

    async def test_create_template(self):
        template = {"name": "Test Template 1", "template": "Template content"}

        saved_template = await self.repository.create_template(template)

        self.assertEqual(1, saved_template["id"])

        post_create = await self.connection.execute(
            "SELECT id, name, template FROM email_template"
        )

        self.assertEqual(
            [(1, "Test Template 1", "Template content")], await post_create.fetchall()
        )

    async def test_update_template(self):
        await self.connection.execute(
            """
            INSERT INTO email_template (id, name, template) VALUES 
            (1, 'Templ 1', 'Templ 1 long content')
            """
        )

        await self.repository.update_template(
            {"id": 1, "name": "Updated 1", "template": "Templ 1 short"}
        )

        post_update = await self.connection.execute(
            "SELECT id, name, template FROM email_template"
        )

        self.assertEqual(
            [(1, "Updated 1", "Templ 1 short")], await post_update.fetchall()
        )

    async def test_get_template(self):
        await self.connection.execute(
            """
            INSERT INTO email_template (id, name, template) VALUES 
            (1, 'Templ 1', 'Templ 1 long content')
            """
        )

        template = await self.repository.get_template(1)

        self.assertEqual(
            {"id": 1, "name": "Templ 1", "template": "Templ 1 long content"}, template
        )

    async def test_list_templates(self):
        await self.connection.execute(
            """
            INSERT INTO email_template (id, name, template) VALUES 
            (1, 'Templ 1', 'Templ 1 long content'),
            (2, 'Templ 2', 'Templ 2 long content'),
            (3, 'Templ 3', 'Templ 3 long content')
            """
        )

        templates = await self.repository.list_templates()

        self.assertEqual(
            [
                {"id": 1, "name": "Templ 1"},
                {"id": 2, "name": "Templ 2"},
                {"id": 3, "name": "Templ 3"},
            ],
            templates,
        )
