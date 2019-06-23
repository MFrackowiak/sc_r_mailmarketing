from asynctest import TestCase, create_autospec

from web.integrations.email_client.abstract import AbstractEmailClient
from web.services.settings.service import SettingsService


class SettingsServiceTestCase(TestCase):
    def setUp(self):
        self._client = create_autospec(AbstractEmailClient)
        self.service = SettingsService(self._client)

    async def test_get_current_settings(self):
        self._client.get_custom_headers_and_email_from.return_value = {
            "headers": {
                "x-customer": "test",
            },
            "email_from": {
                "name": "Noreply Guy",
                "email": "noreply@ur.co",
            }
        }

        success, settings = await self.service.get_current_settings()

        self.assertTrue(success)
        self.assertEqual({
            "headers": {
                "x-customer": "test",
            },
            "email_from": {
                "name": "Noreply Guy",
                "email": "noreply@ur.co",
            },
            "auth": {
                "user": "*****",
                "password": "*****",
            }
        }, settings)
        self._client.get_custom_headers_and_email_from.assert_awaited_once()

    async def test_get_current_settings_validation_error(self):
        pass

    async def test_get_current_settings_unavailable_error(self):
        pass

    async def test_get_current_settings_unexpected_error(self):
        pass