from asyncio import ensure_future, gather, sleep
from typing import List, Dict, Generator, Optional, Tuple

from common.enums import EmailResult
from email_client.integrations.email.abstract import AbstractEmailGatewayClient
from email_client.integrations.web.abstract import AbstractWebClient
from email_client.services.email.abstract import AbstractSendEmailService
from email_client.settings.abstract import AbstractSettingsStorage


class SendEmailService(AbstractSendEmailService):
    def __init__(
        self,
        web_client: AbstractWebClient,
        email_client: AbstractEmailGatewayClient,
        settings_storage: AbstractSettingsStorage,
        batch_size: int = 20,
        retry_count: int = 3,
        retry_backoff: int = 3,
    ):
        self._web_client = web_client
        self._email_client = email_client
        self._settings_storage = settings_storage

        self._batch_size = batch_size
        self._retry_count = retry_count
        self._retry_backoff = retry_backoff

    def dispatch_sending_emails(self, jobs: List[Dict], template: str, subject: str):
        ensure_future(self.send_emails(jobs, template, subject))

    async def send_emails(
        self, jobs: List[Dict], template: str, subject: str, retry_attempt: int = 0
    ):
        auth, headers, email_from = (
            await self._settings_storage.get_gateway_credentials_headers_and_from()
        )
        to_retry = []

        batches = [
            self.send_email_batch(batch, template, subject, auth, headers, email_from)
            for batch in self._split_to_batches(jobs, self._batch_size)
        ]

        results = await gather(*batches)

        for retry in results:
            to_retry.extend(retry)

        if to_retry:
            ensure_future(
                self.manage_retry(to_retry, template, subject, retry_attempt + 1)
            )

    async def manage_retry(
        self, jobs: List[Dict], template: str, subject: str, retry_attempt: int
    ):
        if retry_attempt > self._retry_count:
            await self._web_client.report_job_status(
                {EmailResult.FAILURE: [job["id"] for job in jobs]}
            )
        else:
            await sleep(self._retry_backoff ** retry_attempt)
            await self.send_emails(jobs, template, subject, retry_attempt)

    async def send_email_batch(
        self,
        jobs_batch: List[Dict],
        template: str,
        subject: str,
        auth: Tuple[str, str],
        headers: Optional[Dict],
        email_from: Dict[str, str],
    ) -> List[Dict]:
        results, failed = await self._email_client.send_emails(
            jobs_batch, template, subject, auth, email_from, headers
        )

        await self._web_client.report_job_status(results)

        return failed

    def _split_to_batches(
        self, to_split: List, batch_size: int
    ) -> Generator[List, None, None]:
        count = len(to_split)
        for i in range(0, count, batch_size):
            yield to_split[i : min(i + batch_size, count)]
