from asynctest import TestCase, create_autospec

from common.exceptions import (
    ValidationError,
    UnavailableServiceError,
    UnexpectedServiceError,
)
from web.integrations.email_client.abstract import AbstractEmailClient
from web.services.settings.service import SettingsService


class SettingsServiceTestCase(TestCase):
    def setUp(self):
        self._client = create_autospec(AbstractEmailClient)
        self.service = SettingsService(self._client)

    async def test_get_current_settings(self):
        self._client.get_custom_headers_and_email_from.return_value = {
            "headers": {"x-customer": "test"},
            "email_from": {"name": "Noreply Guy", "email": "noreply@ur.co"},
        }

        success, settings = await self.service.get_current_settings()

        self.assertTrue(success)
        self.assertEqual(
            {
                "headers": {"x-customer": "test"},
                "email_from": {"name": "Noreply Guy", "email": "noreply@ur.co"},
                "auth": {"user": "*****", "password": "*****"},
            },
            settings,
        )
        self._client.get_custom_headers_and_email_from.assert_awaited_once_with()

    async def test_get_current_settings_validation_error(self):
        self._client.get_custom_headers_and_email_from.side_effect = ValidationError(
            "Missing values"
        )

        success, error = await self.service.get_current_settings()

        self.assertFalse(success)
        self.assertEqual(
            error, "Request malformed: Missing values, contact administrator."
        )
        self._client.get_custom_headers_and_email_from.assert_awaited_once_with()

    async def test_get_current_settings_unavailable_error(self):
        self._client.get_custom_headers_and_email_from.side_effect = UnavailableServiceError(
            "No connection"
        )

        success, error = await self.service.get_current_settings()

        self.assertFalse(success)
        self.assertEqual(error, "Email service not available: No connection.")
        self._client.get_custom_headers_and_email_from.assert_awaited_once_with()

    async def test_get_current_settings_unexpected_error(self):
        self._client.get_custom_headers_and_email_from.side_effect = UnexpectedServiceError(
            "Unknown"
        )

        success, error = await self.service.get_current_settings()

        self.assertFalse(success)
        self.assertEqual(error, "Unexpected error occurred: Unknown.")
        self._client.get_custom_headers_and_email_from.assert_awaited_once_with()

    async def test_update_settings(self):
        settings = {
            "headers": {"x-customer": "test"},
            "name": "Noreply Guy",
            "email": "noreply@ur.co",
            "user": "admin",
            "password": "admin1",
        }

        success, error = await self.service.update_settings(settings)

        self.assertTrue(success)
        self.assertIsNone(error)
        self._client.update_email_client_settings.assert_awaited_once_with(
            {
                "headers": {"x-customer": "test"},
                "email_from": {"name": "Noreply Guy", "email": "noreply@ur.co"},
                "auth": {"user": "admin", "password": "admin1"},
            }
        )

    async def test_update_settings_validation_error(self):
        self._client.update_email_client_settings.side_effect = ValidationError(
            "Missing values"
        )
        settings = {
            "headers": {"x-customer": "test"},
            "name": "Noreply Guy",
            "email": "noreply@ur.co",
            "user": "admin",
            "password": "admin1",
        }

        success, error = await self.service.update_settings(settings)

        self.assertFalse(success)
        self.assertEqual(
            error, "Request malformed: Missing values, contact administrator."
        )
        self._client.update_email_client_settings.assert_awaited_once_with(
            {
                "headers": {"x-customer": "test"},
                "email_from": {"name": "Noreply Guy", "email": "noreply@ur.co"},
                "auth": {"user": "admin", "password": "admin1"},
            }
        )

    async def test_update_settings_unavailable_error(self):
        self._client.update_email_client_settings.side_effect = UnavailableServiceError(
            "No connection"
        )
        settings = {
            "headers": {"x-customer": "test"},
            "name": "Noreply Guy",
            "email": "noreply@ur.co",
            "user": "admin",
            "password": "admin1",
        }

        success, error = await self.service.update_settings(settings)

        self.assertFalse(success)
        self.assertEqual(error, "Email service not available: No connection.")
        self._client.update_email_client_settings.assert_awaited_once_with(
            {
                "headers": {"x-customer": "test"},
                "email_from": {"name": "Noreply Guy", "email": "noreply@ur.co"},
                "auth": {"user": "admin", "password": "admin1"},
            }
        )

    async def test_update_settings_unexpected_error(self):
        self._client.update_email_client_settings.side_effect = UnexpectedServiceError(
            "Unknown"
        )
        settings = {
            "headers": {"x-customer": "test"},
            "name": "Noreply Guy",
            "email": "noreply@ur.co",
            "user": "admin",
            "password": "admin1",
        }

        success, error = await self.service.update_settings(settings)

        self.assertFalse(success)
        self.assertEqual(error, "Unexpected error occurred: Unknown.")
        self._client.update_email_client_settings.assert_awaited_once_with(
            {
                "headers": {"x-customer": "test"},
                "email_from": {"name": "Noreply Guy", "email": "noreply@ur.co"},
                "auth": {"user": "admin", "password": "admin1"},
            }
        )
