import json

from asynctest import create_autospec
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

    def test_get(self):
        self.settings_service.get_custom_headers_and_email_from.return_value = {
            "headers": {},
            "email_from": {"name": "Someone", "email": "some@one.co"},
        }

        response = self.fetch("/api/v1/settings")

        self.assertEqual(response.code, 200)
        self.assertEqual(
            json.loads(response.body),
            {"headers": {}, "email_from": {"name": "Someone", "email": "some@one.co"}},
        )
        self.settings_service.get_custom_headers_and_email_from.assert_awaited_once()

    def test_patch_all(self):
        response = self.fetch(
            "/api/v1/settings",
            method="PATCH",
            body=json.dumps(
                {
                    "auth": {"user": "user", "password": "pass"},
                    "email_from": {"name": "User", "email": "admin@co.co"},
                    "headers": {"reply-to": "us <asd@fg.hj>"},
                }
            ),
        )
        self.assertEqual(response.code, 200)

        self.settings_service.update_email_credentials.assert_awaited_once_with(
            user="user", password="pass"
        )
        self.settings_service.update_email_from.assert_awaited_once_with(
            name="User", email="admin@co.co"
        )
        self.settings_service.update_custom_headers.assert_awaited_once_with(
            headers={"reply-to": "us <asd@fg.hj>"}
        )

    def test_partial_patch(self):
        response = self.fetch(
            "/api/v1/settings",
            method="PATCH",
            body=json.dumps({"email_from": {"name": "User", "email": "admin@co.co"}}),
        )
        self.assertEqual(response.code, 200)
        self.settings_service.update_email_credentials.assert_not_awaited()
        self.settings_service.update_email_from.assert_awaited_once_with(
            name="User", email="admin@co.co"
        )
        self.settings_service.update_custom_headers.assert_not_awaited()

    def test_empty_patch(self):
        response = self.fetch("/api/v1/settings", method="PATCH", body=json.dumps(""))
        self.assertEqual(response.code, 400)
        self.settings_service.update_email_credentials.assert_not_awaited()
        self.settings_service.update_email_from.assert_not_awaited()
        self.settings_service.update_custom_headers.assert_not_awaited()
