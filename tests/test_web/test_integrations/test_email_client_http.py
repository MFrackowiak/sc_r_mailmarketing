from asynctest import TestCase, CoroutineMock, Mock

from web.integrations.email_client.http import EmailHTTPClient


class EmailHTTPClientTestCase(TestCase):
    def setUp(self):
        self.session = Mock(
            post=CoroutineMock(), get=CoroutineMock(), patch=CoroutineMock()
        )
        self.client = EmailHTTPClient(self.session, "http://client/")

    async def test_get_custom_headers_and_email_from(self):
        self.session.get.return_value = Mock(
            code=200,
            json=CoroutineMock(
                return_value={
                    "email_from": {"name": "Admin", "email": "some@guy.co"},
                    "headers": {},
                }
            ),
        )

        response = await self.client.get_custom_headers_and_email_from()

        self.assertEqual(
            response,
            {"email_from": {"name": "Admin", "email": "some@guy.co"}, "headers": {}},
        )

        self.session.get.assert_awaited_once_with("http://client/api/v1/settings")

    async def test_update_email_client_settings(self):
        self.session.patch.return_value = Mock(code=200)

        await self.client.update_email_client_settings(
            {
                "email_from": {"name": "Admin", "email": "some@guy.co"},
                "auth": {"user": "admin", "password": "admin1"},
            }
        )

        self.session.patch.assert_awaited_once_with(
            "http://client/api/v1/settings",
            json={
                "email_from": {"name": "Admin", "email": "some@guy.co"},
                "auth": {"user": "admin", "password": "admin1"},
            },
        )

    async def test_schedule_mailing_jobs(self):
        self.session.post.return_value = Mock(code=202)
        jobs = [
            {"id": 1, "name": "username", "email": "admin@co.co"},
            {"id": 2, "name": "username", "email": "admin1@co.co"},
        ]
        template = "Hello {name}!"
        subject = "subject"

        await self.client.schedule_mailing_jobs(jobs, template, subject)

        self.session.post.assert_awaited_once_with(
            "http://client/api/v1/email",
            json={"jobs": jobs, "template": template, "subject": "subject"},
        )
