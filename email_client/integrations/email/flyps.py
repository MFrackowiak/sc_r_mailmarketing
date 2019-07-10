import traceback
from asyncio import gather
from collections import defaultdict
from logging import getLogger
from typing import List, Dict, Optional, Tuple

from aiohttp import ClientSession, BasicAuth

from common.enums import EmailResult
from email_client.integrations.email.abstract import AbstractEmailGatewayClient


logger = getLogger(__name__)


class FlypsGatewayClient(AbstractEmailGatewayClient):
    def __init__(self, gateway_url: str, session: ClientSession):
        self._gateway_url = gateway_url
        self._session = session

    async def send_emails(
        self,
        jobs: List[Dict],
        template: str,
        subject: str,
        auth: Tuple[str, str],
        email_from: Dict[str, str],
        headers: Optional[Dict] = None,
    ) -> Tuple[Dict, List[Dict]]:
        results = await gather(
            *[
                self._send_email(
                    job, template, subject, auth, email_from, headers or {}
                )
                for job in jobs
            ]
        )
        results_grouped = defaultdict(list)
        retry_jobs = []

        for (result, message_id), job in zip(results, jobs):
            if result == EmailResult.RECOVERABLE_FAILURE:
                retry_jobs.append(job)
            if result == EmailResult.SUCCESS:
                results_grouped[result].append(
                    {"id": job["id"], "message_id": message_id}
                )
            else:
                results_grouped[result].append({"id": job["id"], "message_id": ""})

        return results_grouped, retry_jobs

    async def _send_email(
        self,
        job: Dict,
        template: str,
        subject: str,
        auth: Tuple[str, str],
        email_from: Dict[str, str],
        headers: Dict,
    ) -> Tuple[EmailResult, Optional[str]]:
        try:
            auth = BasicAuth(*auth, encoding="UTF-8")
        except (ValueError, TypeError):
            return EmailResult.AUTH_FAILURE, None

        try:
            response = await self._session.post(
                self._gateway_url,
                json={
                    "from": email_from,
                    "to": {
                        "name": job.get("name", job["email"]),
                        "email": job["email"],
                    },
                    "subject": subject,
                    "text": self.render_template(job, template),
                    "headers": headers,
                },
                auth=auth,
            )
            if response.status == 202:
                response_json = await response.json()
                return EmailResult.SUCCESS, response_json["message_id"]
            elif response.status == 401:
                return EmailResult.AUTH_FAILURE, None
            elif response.status == 400:
                return EmailResult.FAILURE, None
        except (TimeoutError, ConnectionError):
            logger.warning(
                f"Error with connection when trying to send job {job['id']}: "
                f"{traceback.format_exc()}"
            )
        except Exception:
            logger.error(
                f"Unexpected error when trying to send job {job['id']}: "
                f"{traceback.format_exc()}"
            )
        return EmailResult.RECOVERABLE_FAILURE, None

    def render_template(self, job: Dict, template: str):
        return template.format(**job)
