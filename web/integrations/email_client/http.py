from typing import List, Dict

from aiohttp import ClientSession

from common.decorators import catch_timeout
from web.integrations.email_client.abstract import AbstractEmailClient
from web.integrations.http import BaseHTTPClient


class ClientError(Exception):
    pass


class EmailHTTPClient(AbstractEmailClient, BaseHTTPClient):
    SETTINGS_ENDPOINT = "api/v1/settings"
    EMAIL_ENDPOINT = "api/v1/email"

    def __init__(self, session: ClientSession, base_url: str):
        self._session = session
        self._base_url = base_url

    @catch_timeout
    async def get_custom_headers_and_email_from(self) -> Dict:
        response = await self._session.get(f"{self._base_url}{self.SETTINGS_ENDPOINT}")

        if response.status != 200:
            await self._raise_for_code(response)

        return await response.json()

    @catch_timeout
    async def update_email_client_settings(self, settings: Dict):
        response = await self._session.patch(
            f"{self._base_url}{self.SETTINGS_ENDPOINT}", json=settings
        )

        if response.status != 200:
            await self._raise_for_code(response)

    @catch_timeout
    async def schedule_mailing_jobs(
        self, jobs: List[Dict], template: str, subject: str
    ):
        response = await self._session.post(
            f"{self._base_url}{self.EMAIL_ENDPOINT}",
            json={"jobs": jobs, "template": template, "subject": subject},
        )

        if response.status != 202:
            await self._raise_for_code(response)
