from tests.test_web.test_repositories.aiopg_base import AioPGBaseTestCase
from web.repositories.contact.aiopg import SimplePostgresContactRepository


class AioPGContactRepositoryTestCase(AioPGBaseTestCase):
    async def setUp(self):
        await super().setUp()
        self.repository = SimplePostgresContactRepository(self.db_engine_mock)

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

        test_tuples = await self.connection.execute(
            "SELECT id, name, first_name, last_name, email FROM contact"
        )

        self.assertEqual(
            [(1, "User1", "Janusz", "Kowalski", "jk@co.co")],
            await test_tuples.fetchall(),
        )

    async def test_get_contact_with_segments(self):
        await self.connection.execute(
            """
            INSERT INTO contact (id, name, first_name, last_name, email)
            VALUES (1, 'User1', 'Janusz', 'Kowalski', 'jk@co.co')
            """
        )
        await self.connection.execute(
            """
            INSERT INTO segment (id, name) VALUES
            (1, 'Users'), (2, 'Testers'), (3, 'Beta')
            """
        )
        await self.connection.execute(
            """
            INSERT INTO segment_contact (contact_id, segment_id) 
            VALUES (1, 1), (1, 2)
            """
        )

        contact, segments = await self.repository.get_contact_with_segments(1)

        self.assertEqual(
            {
                "name": "User1",
                "first_name": "Janusz",
                "last_name": "Kowalski",
                "email": "jk@co.co",
                "id": 1,
            },
            contact,
        )
        self.assertEqual(
            [{"id": 1, "name": "Users"}, {"id": 2, "name": "Testers"}], segments
        )

    async def test_read_contacts(self):
        await self.connection.execute(
            """
            INSERT INTO contact (id, name, first_name, last_name, email)
            VALUES
            (1, 'User1', 'Janusz', 'Kowalski', 'jk1@co.co'),
            (2, 'User2', 'Janusz', 'Kowalski', 'jk2@co.co'),
            (3, 'User3', 'Janusz', 'Kowalski', 'jk3@co.co'),
            (4, 'User4', 'Janusz', 'Kowalski', 'jk4@co.co'),
            (5, 'User5', 'Janusz', 'Kowalski', 'jk5@co.co')
            """
        )

        first_page = await self.repository.read_contacts(0, 4)

        self.assertEqual(
            [
                {
                    "name": "User1",
                    "first_name": "Janusz",
                    "last_name": "Kowalski",
                    "email": "jk1@co.co",
                    "id": 1,
                },
                {
                    "name": "User2",
                    "first_name": "Janusz",
                    "last_name": "Kowalski",
                    "email": "jk2@co.co",
                    "id": 2,
                },
                {
                    "name": "User3",
                    "first_name": "Janusz",
                    "last_name": "Kowalski",
                    "email": "jk3@co.co",
                    "id": 3,
                },
                {
                    "name": "User4",
                    "first_name": "Janusz",
                    "last_name": "Kowalski",
                    "email": "jk4@co.co",
                    "id": 4,
                },
            ],
            first_page,
        )

        second_page = await self.repository.read_contacts(1, 4)

        self.assertEqual(
            [
                {
                    "name": "User5",
                    "first_name": "Janusz",
                    "last_name": "Kowalski",
                    "email": "jk5@co.co",
                    "id": 5,
                }
            ],
            second_page,
        )

        self.assertEqual([], await self.repository.read_contacts(2, 4))

    async def test_update_contact(self):
        await self.connection.execute(
            """
            INSERT INTO contact (id, name, first_name, last_name, email)
            VALUES (1, 'User1', 'Janusz', 'Kowalski', 'jk@co.co')
            """
        )

        await self.repository.update_contact(
            {
                "id": 1,
                "first_name": "Jan",
                "last_name": "Nowak",
                "email": "jn@co.co",
                "name": "User1",
            }
        )

        modified = await self.connection.execute(
            """
            SELECT id, name, first_name, last_name, email FROM contact
            """
        )
        self.assertEqual(
            (1, "User1", "Jan", "Nowak", "jn@co.co"), await modified.fetchone()
        )

    async def test_delete_contact(self):
        await self.connection.execute(
            """
            INSERT INTO contact (id, name, first_name, last_name, email)
            VALUES (1, 'User1', 'Janusz', 'Kowalski', 'jk@co.co')
            """
        )

        await self.repository.delete_contact(1)

        contacts = await self.connection.execute(
            """
            SELECT id, name, first_name, last_name, email FROM contact
            """
        )
        self.assertEqual([], await contacts.fetchall())

    async def test_create_segment(self):
        result = await self.repository.create_segment({"name": "Testers"})

        self.assertEqual({"name": "Testers", "id": 1}, result)

        segments = await self.connection.execute(
            """
            SELECT id, name FROM segment
            """
        )
        self.assertEqual([(1, "Testers")], await segments.fetchall())

    async def test_get_segment(self):
        await self.connection.execute(
            """
            INSERT INTO segment (id, name) VALUES (1, 'test-seg')
            """
        )

        segment = await self.repository.get_segment(1)

        self.assertEqual({"id": 1, "name": "test-seg"}, segment)

    async def test_read_segments(self):
        await self.connection.execute(
            """
            INSERT INTO segment (id, name)
            VALUES (1, 'test-seg'), (2, 'beta'), (3, 'alpha')
            """
        )

        first_page = await self.repository.read_segments(0, 2)

        self.assertEqual(
            [{"id": 1, "name": "test-seg"}, {"id": 2, "name": "beta"}], first_page
        )

        second_page = await self.repository.read_segments(1, 2)

        self.assertEqual([{"id": 3, "name": "alpha"}], second_page)

        third_page = await self.repository.read_segments(2, 2)

        self.assertEqual([], third_page)

    async def test_update_segment(self):
        await self.connection.execute(
            """
            INSERT INTO segment (id, name) VALUES (1, 'test-seg')
            """
        )

        await self.repository.update_segment({"id": 1, "name": "happy-seg"})

        updated_segment = await self.connection.execute(
            "SELECT name FROM segment WHERE id = 1"
        )

        self.assertEqual("happy-seg", await updated_segment.scalar())

    async def test_delete_segment(self):
        await self.connection.execute(
            """
            INSERT INTO segment (id, name) VALUES (1, 'test-seg')
            """
        )

        await self.repository.delete_segment(1)

        segments = await self.connection.execute("SELECT name FROM segment")

        self.assertEqual([], await segments.fetchall())

    async def test_list_contacts_in_segment(self):
        await self.connection.execute(
            """
            INSERT INTO segment (id, name) VALUES (1, 'test-seg')
            """
        )
        await self.connection.execute(
            """
            INSERT INTO contact (id, name, email, first_name, last_name)
            VALUES
            (1, 'User1', 'user1@co.oc', '', ''),
            (2, 'User2', 'user2@co.oc', '', ''),
            (3, 'User3', 'user3@co.oc', '', ''),
            (4, 'User4', 'user4@co.oc', '', '')
            """
        )
        await self.connection.execute(
            """
            INSERT INTO segment_contact (contact_id, segment_id)
            VALUES (1, 1), (3, 1), (4, 1)
            """
        )

        segment_contacts = await self.repository.list_contacts_in_segment(1)

        self.assertEqual(
            [
                {"id": 1, "name": "User1", "email": "user1@co.oc"},
                {"id": 3, "name": "User3", "email": "user3@co.oc"},
                {"id": 4, "name": "User4", "email": "user4@co.oc"},
            ],
            segment_contacts,
        )

    async def test_add_contact_to_segment(self):
        await self.connection.execute(
            """
            INSERT INTO segment (id, name) VALUES (1, 'test-seg')
            """
        )
        await self.connection.execute(
            """
            INSERT INTO contact (id, name, email, first_name, last_name)
            VALUES
            (1, 'User1', 'user1@co.oc', '', ''),
            (2, 'User2', 'user2@co.oc', '', '')
            """
        )

        await self.repository.add_contact_to_segment(1, 2)

        result = await self.connection.execute(
            "SELECT contact_id, segment_id FROM segment_contact"
        )

        self.assertEqual([(2, 1)], await result.fetchall())

    async def test_remoce_contact_from_segment(self):
        await self.connection.execute(
            """
            INSERT INTO segment (id, name) VALUES (1, 'test-seg')
            """
        )
        await self.connection.execute(
            """
            INSERT INTO contact (id, name, email, first_name, last_name)
            VALUES
            (1, 'User1', 'user1@co.oc', '', ''),
            (2, 'User2', 'user2@co.oc', '', '')
            """
        )
        await self.connection.execute(
            """
            INSERT INTO segment_contact (contact_id, segment_id)
            VALUES (1, 1), (2, 1)
            """
        )

        await self.repository.remove_contact_from_segment(1, 2)

        result = await self.connection.execute(
            "SELECT contact_id, segment_id FROM segment_contact"
        )

        self.assertEqual([(1, 1)], await result.fetchall())

    async def test_get_contacts_count(self):
        await self.connection.execute(
            """
            INSERT INTO contact (id, name, first_name, last_name, email)
            VALUES
            (1, 'User1', 'Janusz', 'Kowalski', 'jk1@co.co'),
            (2, 'User2', 'Janusz', 'Kowalski', 'jk2@co.co'),
            (3, 'User3', 'Janusz', 'Kowalski', 'jk3@co.co'),
            (4, 'User4', 'Janusz', 'Kowalski', 'jk4@co.co'),
            (5, 'User5', 'Janusz', 'Kowalski', 'jk5@co.co')
            """
        )

        self.assertEqual(5, await self.repository.get_contacts_count())

    async def test_get_segments_count(self):
        await self.connection.execute(
            """
            INSERT INTO segment (id, name)
            VALUES
            (1, 'Segment1'),
            (2, 'Segment2'),
            (3, 'Segment3'),
            (4, 'Segment4'),
            (5, 'Segment5')
            """
        )

        self.assertEqual(5, await self.repository.get_segments_count())
