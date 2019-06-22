import traceback
from asyncio import sleep
from logging import getLogger
from typing import Dict, List

from aiohttp import ClientSession

from email_client.integrations.email.abstract import EmailResult
from email_client.integrations.web.abstract import AbstractWebClient


logger = getLogger(__name__)


class WebClient(AbstractWebClient):
    def __init__(
        self,
        web_url: str,
        session: ClientSession,
        retry_count: int = 3,
        retry_backoff: int = 3,
    ):
        self._web_url = web_url
        self._session = session

        self._retry_count = retry_count
        self._retry_backoff = retry_backoff

    async def report_job_status(self, statuses: Dict[EmailResult, List[int]]):
        payload = {status.value: value for status, value in statuses.items()}

        for i in range(self._retry_count + 1):
            if i > 0:
                await sleep(self._retry_backoff ** i)

            try:
                response = await self._session.post(self._web_url, json=payload)
                if response.status == 200:
                    return
            except (TimeoutError, ConnectionError):
                logger.warning(
                    f"Error with connection when trying to send job updates: "
                    f"{traceback.format_exc()}"
                )
            except Exception:
                logger.error(
                    f"Unexpected error when trying to send job updates: "
                    f"{traceback.format_exc()}"
                )

        logger.critical(f"Could not contact web to report job updates: {statuses}")
