from typing import Dict

from email_client.services.settings.abstract import AbstractSettingsService
from email_client.settings.abstract import AbstractSettingsStorage


class SettingsService(AbstractSettingsService):
    def __init__(self, storage: AbstractSettingsStorage):
        self._storage = storage

    async def get_custom_headers_and_email_from(self) -> Dict:
        return {
            "headers": await self._storage.get_custom_headers(),
            "from": await self._storage.get_email_from(),
        }

    async def update_email_credentials(self, user: str, password: str):
        await self._storage.save_gateway_credentials(user, password)

    async def update_custom_headers(self, headers: Dict):
        await self._storage.save_custom_headers(headers)

    async def update_email_from(self, name: str, email: str):
        await self._storage.save_email_from(name, email)
