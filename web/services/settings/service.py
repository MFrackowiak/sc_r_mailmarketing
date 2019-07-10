from typing import Dict, Tuple, Union, Optional

from common.exceptions import (
    ValidationError,
    UnavailableServiceError,
    UnexpectedServiceError,
)
from web.integrations.email_client.abstract import AbstractEmailClient
from web.services.settings.abstract import AbstractSettingsService


class SettingsService(AbstractSettingsService):
    def __init__(self, client: AbstractEmailClient):
        self._client = client

    async def get_current_settings(self) -> Tuple[bool, Union[Dict, str]]:
        error = None

        try:
            settings = await self._client.get_custom_headers_and_email_from()
        except ValidationError as e:
            error = f"Request malformed: {e}, contact administrator."
        except UnavailableServiceError as e:
            error = f"Email service not available: {e}."
        except UnexpectedServiceError as e:
            error = f"Unexpected error occurred: {e}."

        return (
            not error,
            (
                error
                if error
                else {"auth": {"user": "*****", "password": "*****"}, **settings}
            ),
        )

    async def update_settings(self, settings: Dict) -> Tuple[bool, Optional[str]]:
        formatted_settings = {}

        if {"user", "password"}.issubset(settings):
            formatted_settings["auth"] = {
                "user": settings["user"],
                "password": settings["password"],
            }

        if {"name", "email"}.issubset(settings):
            formatted_settings["email_from"] = {
                "name": settings["name"],
                "email": settings["email"],
            }

        if "headers" in settings:
            formatted_settings["headers"] = settings["headers"]

        try:
            await self._client.update_email_client_settings(formatted_settings)
            return True, None
        except ValidationError as e:
            error = f"Request malformed: {e}, contact administrator."
        except UnavailableServiceError as e:
            error = f"Email service not available: {e}."
        except UnexpectedServiceError as e:
            error = f"Unexpected error occurred: {e}."

        return False, error
