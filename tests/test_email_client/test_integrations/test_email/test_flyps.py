from aiohttp import BasicAuth
from asynctest import TestCase, CoroutineMock, patch, call, Mock, MagicMock

from common.enums import EmailResult
from email_client.integrations.email.flyps import FlypsGatewayClient


class FlypsGatewayClientTestCase(TestCase):
    def setUp(self):
        self.session = Mock(post=CoroutineMock())

    async def test_send_emails(self):
        send_email_mock = CoroutineMock(
            side_effect=[
                (
                    EmailResult.SUCCESS,
                    "<4370c0c3-c52f-42a0-9087-b73fd4ce149f@example.flypsdm.io>",
                ),
                (EmailResult.FAILURE, None),
                (EmailResult.AUTH_FAILURE, None),
                (
                    EmailResult.SUCCESS,
                    "<4370c0c4-c52f-42a0-9087-b73fd4ce149f@example.flypsdm.io>",
                ),
                (EmailResult.RECOVERABLE_FAILURE, None),
            ]
        )
        client = FlypsGatewayClient("http://test.co", self.session)
        send_email_patch = patch.object(client, "_send_email", send_email_mock)
        jobs = [
            {"id": 132, "email": "test_1@te.st", "first_name": "Janusz"},
            {"id": 133, "email": "test_2@te.st", "first_name": "Jan"},
            {"id": 134, "email": "test_3@te.st", "first_name": "Janina"},
            {"id": 135, "email": "test_4@te.st", "first_name": "Janusz"},
            {"id": 136, "email": "test_5@te.st", "first_name": "Frida"},
        ]
        auth = ("admin", "admin1")
        headers = {"reply-to": "admin <admin@test.co>"}
        email_from = {"name": "Admin", "email": "admin@co.oc"}
        template = "Hi! This is an email."
        subject = "Subject"

        with send_email_patch:
            results, retry = await client.send_emails(
                jobs, template, subject, auth, email_from, headers
            )

        self.assertEqual(
            results,
            {
                EmailResult.SUCCESS: [
                    {
                        "id": 132,
                        "message_id": "<4370c0c3-c52f-42a0-9087-b73fd4ce149f@example.flypsdm.io>",
                    },
                    {
                        "id": 135,
                        "message_id": "<4370c0c4-c52f-42a0-9087-b73fd4ce149f@example.flypsdm.io>",
                    },
                ],
                EmailResult.FAILURE: [133],
                EmailResult.RECOVERABLE_FAILURE: [136],
                EmailResult.AUTH_FAILURE: [134],
            },
        )
        self.assertEqual(
            retry, [{"id": 136, "email": "test_5@te.st", "first_name": "Frida"}]
        )
        send_email_mock.assert_has_awaits(
            [call(job, template, subject, auth, email_from, headers) for job in jobs]
        )

    async def test_send_email_202(self):
        job = {"id": 14573, "name": "User", "email": "user@co.co", "subject": "Hello!"}
        template = "Hello {name}! Welcome in our subscription."
        subject = "Subject"
        self.session.post.return_value = Mock(
            status=202,
            json=CoroutineMock(
                return_value={
                    "message_id": "<4370c0c4-c52f-42a0-9087-b73fd4ce149f@example.flypsdm.io>"
                }
            ),
        )

        client = FlypsGatewayClient("http://test.co", self.session)
        result, message_id = await client._send_email(
            job,
            template,
            subject,
            ("user", "admin1"),
            {"email": "admin@co.co", "name": "Admin"},
            {},
        )

        self.assertEqual(result, EmailResult.SUCCESS)
        self.assertEqual(
            message_id, "<4370c0c4-c52f-42a0-9087-b73fd4ce149f@example.flypsdm.io>"
        )

        self.session.post.assert_awaited_once_with(
            "http://test.co",
            json={
                "from": {"email": "admin@co.co", "name": "Admin"},
                "to": {"name": "User", "email": "user@co.co"},
                "subject": "Subject",
                "text": "Hello User! Welcome in our subscription.",
                "headers": {},
            },
            auth=BasicAuth("user", "admin1"),
        )

    async def test_send_email_400(self):
        job = {"id": 14573, "name": "User", "email": "user@co.co", "subject": "Hello!"}
        template = "Hello {name}! Welcome in our subscription."
        self.session.post.return_value = Mock(status=400)

        client = FlypsGatewayClient("http://test.co", self.session)
        result, message_id = await client._send_email(
            job,
            template,
            "Subject",
            ("user", "admin1"),
            {"email": "admin@co.co", "name": "Admin"},
            {},
        )

        self.assertEqual(result, EmailResult.FAILURE)
        self.assertIsNone(message_id)

        self.session.post.assert_awaited_once_with(
            "http://test.co",
            json={
                "from": {"email": "admin@co.co", "name": "Admin"},
                "to": {"name": "User", "email": "user@co.co"},
                "subject": "Subject",
                "text": "Hello User! Welcome in our subscription.",
                "headers": {},
            },
            auth=BasicAuth("user", "admin1"),
        )

    async def test_send_email_401(self):
        job = {"id": 14573, "name": "User", "email": "user@co.co", "subject": "Hello!"}
        template = "Hello {name}! Welcome in our subscription."
        self.session.post.return_value = Mock(status=401)

        client = FlypsGatewayClient("http://test.co", self.session)
        result, message_id = await client._send_email(
            job,
            template,
            "Subject",
            ("user", "admin1"),
            {"email": "admin@co.co", "name": "Admin"},
            {},
        )

        self.assertEqual(result, EmailResult.AUTH_FAILURE)
        self.assertIsNone(message_id)

        self.session.post.assert_awaited_once_with(
            "http://test.co",
            json={
                "from": {"email": "admin@co.co", "name": "Admin"},
                "to": {"name": "User", "email": "user@co.co"},
                "subject": "Subject",
                "text": "Hello User! Welcome in our subscription.",
                "headers": {},
            },
            auth=BasicAuth("user", "admin1"),
        )

    async def test_send_email_500(self):
        job = {"id": 14573, "name": "User", "email": "user@co.co", "subject": "Hello!"}
        template = "Hello {name}! Welcome in our subscription."
        self.session.post.return_value = Mock(status=500)

        client = FlypsGatewayClient("http://test.co", self.session)
        result, message_id = await client._send_email(
            job,
            template,
            "Subject",
            ("user", "admin1"),
            {"email": "admin@co.co", "name": "Admin"},
            {},
        )

        self.assertEqual(result, EmailResult.RECOVERABLE_FAILURE)
        self.assertIsNone(message_id)

        self.session.post.assert_awaited_once_with(
            "http://test.co",
            json={
                "from": {"email": "admin@co.co", "name": "Admin"},
                "to": {"name": "User", "email": "user@co.co"},
                "subject": "Subject",
                "text": "Hello User! Welcome in our subscription.",
                "headers": {},
            },
            auth=BasicAuth("user", "admin1"),
        )

    @patch("email_client.integrations.email.flyps.logger")
    async def test_send_email_timeout(self, logger_mock: MagicMock):
        job = {"id": 14573, "name": "User", "email": "user@co.co", "subject": "Hello!"}
        template = "Hello {name}! Welcome in our subscription."
        self.session.post.side_effect = TimeoutError()

        client = FlypsGatewayClient("http://test.co", self.session)
        result, message_id = await client._send_email(
            job,
            template,
            "Subject",
            ("user", "admin1"),
            {"email": "admin@co.co", "name": "Admin"},
            {},
        )

        self.assertEqual(result, EmailResult.RECOVERABLE_FAILURE)
        self.assertIsNone(message_id)

        logger_mock.warning.assert_called_once()
        self.session.post.assert_awaited_once_with(
            "http://test.co",
            json={
                "from": {"email": "admin@co.co", "name": "Admin"},
                "to": {"name": "User", "email": "user@co.co"},
                "subject": "Subject",
                "text": "Hello User! Welcome in our subscription.",
                "headers": {},
            },
            auth=BasicAuth("user", "admin1"),
        )

    @patch("email_client.integrations.email.flyps.logger")
    async def test_send_email_other_exception(self, logger_mock: MagicMock):
        job = {"id": 14573, "name": "User", "email": "user@co.co", "subject": "Hello!"}
        template = "Hello {name}! Welcome in our subscription."
        self.session.post.side_effect = ValueError("No one expected me")

        client = FlypsGatewayClient("http://test.co", self.session)
        result, message_id = await client._send_email(
            job,
            template,
            "Subject",
            ("user", "admin1"),
            {"email": "admin@co.co", "name": "Admin"},
            {},
        )

        self.assertEqual(result, EmailResult.RECOVERABLE_FAILURE)
        self.assertIsNone(message_id)

        logger_mock.error.assert_called_once()
        self.session.post.assert_awaited_once_with(
            "http://test.co",
            json={
                "from": {"email": "admin@co.co", "name": "Admin"},
                "to": {"name": "User", "email": "user@co.co"},
                "subject": "Subject",
                "text": "Hello User! Welcome in our subscription.",
                "headers": {},
            },
            auth=BasicAuth("user", "admin1"),
        )
