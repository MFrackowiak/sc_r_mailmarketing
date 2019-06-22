import json

from asynctest import create_autospec, patch, MagicMock
from tornado.testing import AsyncHTTPTestCase

from email_client.app import make_app
from email_client.services.email.abstract import AbstractSendEmailService
from email_client.services.settings.abstract import AbstractSettingsService


class TestEmailHandler(AsyncHTTPTestCase):
    def setUp(self):
        self.email_service = create_autospec(AbstractSendEmailService)
        self.settings_service = create_autospec(AbstractSettingsService)
        super().setUp()

    def get_app(self):
        return make_app(self.settings_service, self.email_service)

    @patch("email_client.controllers.email.ensure_future")
    def test_post(self, ensure_future_mock: MagicMock):
        response = self.fetch(
            "/api/v1/email",
            method="POST",
            body=json.dumps(
                {
                    "jobs": [
                        {"id": 13, "subject": "None", "email": "guy@co.co"},
                        {"id": 14, "subject": "None", "email": "other@co.co"},
                    ],
                    "template": "Hello!",
                }
            ),
        )
        self.assertEqual(response.code, 202)
        ensure_future_mock.assert_called_once_with(
            self.email_service.send_emails.return_value
        )
        self.email_service.send_emails.assert_called_once_with(
            jobs=[
                {"id": 13, "subject": "None", "email": "guy@co.co"},
                {"id": 14, "subject": "None", "email": "other@co.co"},
            ],
            template="Hello!",
        )
