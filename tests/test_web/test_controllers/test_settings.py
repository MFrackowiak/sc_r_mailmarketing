from urllib.parse import urlencode

from tests.test_web.test_controllers.base import BaseHandlerTest


class TestSettingsHandlers(BaseHandlerTest):
    def test_post_update_all(self):
        self.settings_service.update_settings.return_value = True, ""
        self.settings_service.get_current_settings.return_value = (
            True,
            {
                "from": {"name": "test", "email": "test@test.co"},
                "auth": {"user": "*****", "password": "******"},
            },
        )

        response = self.fetch(
            "/settings",
            method="POST",
            body=urlencode(
                {
                    "name": "test",
                    "email": "test@test.co",
                    "user": "admin",
                    "password": "admin1",
                }
            ),
        )

        self.assertEqual(response.code, 200)
        self.settings_service.update_settings.assert_awaited_once_with(
            {
                "name": "test",
                "email": "test@test.co",
                "user": "admin",
                "password": "admin1",
            }
        )
        self.settings_service.get_current_settings.assert_awaited_once()
        self.template_loader.load.assert_called_once_with("settings/form.html")
        self.template_loader.load.return_value.generate.assert_called_once_with(
            initial={
                "from": {"name": "test", "email": "test@test.co"},
                "auth": {"user": "*****", "password": "******"},
            }
        )

    def test_post_error(self):
        self.settings_service.update_settings.return_value = False, "Connection timeout"

        response = self.fetch(
            "/settings",
            method="POST",
            body=urlencode(
                {
                    "name": "test",
                    "email": "test@test.co",
                    "user": "admin",
                    "password": "admin1",
                }
            ),
        )

        self.assertEqual(response.code, 500)
        self.template_loader.load.assert_called_once_with("error.html")
        self.template_loader.load.return_value.generate.assert_called_once_with(
            error="Connection timeout"
        )

    def test_get(self):
        self.settings_service.get_current_settings.return_value = (
            True,
            {
                "from": {"name": "test", "email": "test@test.co"},
                "auth": {"user": "*****", "password": "******"},
            },
        )

        response = self.fetch("/settings", method="GET")

        self.assertEqual(response.code, 200)
        self.settings_service.get_current_settings.assert_awaited_once()
        self.template_loader.load.assert_called_once_with("settings/form.html")
        self.template_loader.load.return_value.generate.assert_called_once_with(
            initial={
                "from": {"name": "test", "email": "test@test.co"},
                "auth": {"user": "*****", "password": "******"},
            }
        )

    def test_get_error(self):
        self.settings_service.get_current_settings.return_value = (
            False,
            "Connection timeout",
        )

        response = self.fetch("/settings", method="GET")

        self.assertEqual(response.code, 500)
        self.template_loader.load.assert_called_once_with("error.html")
        self.template_loader.load.return_value.generate.assert_called_once_with(
            error="Connection timeout"
        )
