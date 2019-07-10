from asynctest import TestCase, create_autospec

from email_client.services.settings.service import SettingsService
from email_client.settings.abstract import AbstractSettingsStorage


class SettingsServiceTestCase(TestCase):
    def setUp(self):
        self.settings_storage = create_autospec(AbstractSettingsStorage)

    async def test_get_customer_headers(self):
        service = SettingsService(self.settings_storage)
        self.settings_storage.get_custom_headers.return_value = {
            "reply-to": "Admin <admin@co.co>"
        }
        self.settings_storage.get_email_from.return_value = {
            "name": "Admin",
            "email": "admin@.co.co",
        }

        result = await service.get_custom_headers_and_email_from()

        self.assertEqual(
            result,
            {
                "headers": {"reply-to": "Admin <admin@co.co>"},
                "from": {"name": "Admin", "email": "admin@.co.co"},
            },
        )
        self.settings_storage.get_custom_headers.assert_awaited_once()

    async def test_update_email_credentials(self):
        service = SettingsService(self.settings_storage)

        await service.update_email_credentials("admin", "admin1")

        self.settings_storage.save_gateway_credentials.assert_awaited_once_with(
            "admin", "admin1"
        )

    async def test_update_custom_headers(self):
        service = SettingsService(self.settings_storage)

        await service.update_custom_headers({"from": "admin <admin1@co.co"})

        self.settings_storage.save_custom_headers.assert_awaited_once_with(
            {"from": "admin <admin1@co.co"}
        )
