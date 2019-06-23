from typing import Dict

from common.exceptions import (
    ValidationError,
    UnavailableServiceError,
    UnexpectedServiceError,
)
from web.integrations.email_client.http import EmailHTTPClient
from web.repositories.jobs.abstract import AbstractJobRepository
from web.repositories.templates.abstract import AbstractTemplateRepository
from web.services.email.abstract import AbstractEmailService


class EmailService(AbstractEmailService):
    def __init__(
        self,
        job_repository: AbstractJobRepository,
        template_repository: AbstractTemplateRepository,
        email_client: EmailHTTPClient,
    ):
        self._job_repository = job_repository
        self._template_repository = template_repository
        self._email_client = email_client

    async def send_emails(self, segment_id: int, template_id: int, subject: str):
        created_request_id, jobs = await self._job_repository.create_email_request(
            segment_id, template_id, subject
        )
        template = await self._template_repository.get_email_template(template_id)
        error = None

        try:
            await self._email_client.schedule_mailing_jobs(
                jobs, template["template"], subject
            )
        except ValidationError as e:
            error = f"Request malformed: {e}, contact administrator."
        except UnavailableServiceError as e:
            error = f"Email service not available: {e}."
        except UnexpectedServiceError as e:
            error = f"Unexpected error occurred: {e}."

        return created_request_id, error

    async def get_email_requests(self):
        return await self._job_repository.get_email_requests()

    async def get_email_request_details(self, request_id: int):
        request_details = await self._job_repository.get_email_request(request_id)
        jobs = await self._job_repository.get_email_requests_job_statuses(request_id)

        return {"request": request_details, "jobs": jobs}

    async def update_jobs_statuses(self, statuses: Dict):
        return await self._job_repository.update_job_statuses(statuses)
