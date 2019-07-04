from asynctest import TestCase, create_autospec

from common.enums import EmailResult
from common.exceptions import (
    UnavailableServiceError,
    UnexpectedServiceError,
    ValidationError,
)
from web.integrations.email_client.abstract import AbstractEmailClient
from web.repositories.jobs.abstract import AbstractJobRepository
from web.repositories.templates.abstract import AbstractTemplateRepository
from web.services.email.service import EmailService


class EmailServiceTestCase(TestCase):
    def setUp(self):
        self._job_repo = create_autospec(AbstractJobRepository)
        self._template_repo = create_autospec(AbstractTemplateRepository)
        self._email_client = create_autospec(AbstractEmailClient)

        self.service = EmailService(
            self._job_repo, self._template_repo, self._email_client
        )

        self._jobs = [
            {"id": 145, "contact_id": 12, "name": "User1", "email": "user1@co.co"},
            {"id": 146, "contact_id": 13, "name": "User1", "email": "user1@co.co"},
            {"id": 147, "contact_id": 14, "name": "User1", "email": "user1@co.co"},
        ]
        self._job_repo.create_email_request.return_value = {
            "id": 42,
            "template_id": 213,
            "segment_id": 189,
            "name": "Take a look at a new feature",
        }
        self._job_repo.get_email_requests_job_statuses.return_value = self._jobs
        self._template_repo.get_email_template.return_value = {
            "id": 213,
            "name": "Feature email",
            "template": "Click and see for yourself.",
        }

    async def test_send_emails(self):
        result = await self.service.send_emails(
            189, 213, "Take a look at a new feature"
        )

        self.assertEqual(
            (
                {
                    "id": 42,
                    "template_id": 213,
                    "segment_id": 189,
                    "name": "Take a look at a new feature",
                },
                None,
            ),
            result,
        )
        self._job_repo.create_email_request.assert_awaited_once_with(
            189, 213, "Take a look at a new feature"
        )
        self._job_repo.get_email_requests_job_statuses.assert_awaited_once_with(42)
        self._email_client.schedule_mailing_jobs.assert_awaited_once_with(
            self._jobs, "Click and see for yourself.", "Take a look at a new feature"
        )

    async def test_send_emails_validation_error(self):
        self._email_client.schedule_mailing_jobs.side_effect = ValidationError(
            "Expected str, not int"
        )

        result = await self.service.send_emails(
            189, 213, "Take a look at a new feature"
        )

        self.assertEqual(
            (
                {
                    "id": 42,
                    "template_id": 213,
                    "segment_id": 189,
                    "name": "Take a look at a new feature",
                },
                "Request malformed: Expected str, not int, contact administrator.",
            ),
            result,
        )
        self._job_repo.create_email_request.assert_awaited_once_with(
            189, 213, "Take a look at a new feature"
        )
        self._email_client.schedule_mailing_jobs.assert_awaited_once_with(
            self._jobs, "Click and see for yourself.", "Take a look at a new feature"
        )

    async def test_send_emails_unavailable_service_error(self):
        self._email_client.schedule_mailing_jobs.side_effect = UnavailableServiceError(
            "Unknown reason"
        )

        result = await self.service.send_emails(
            189, 213, "Take a look at a new feature"
        )

        self.assertEqual(
            (
                {
                    "id": 42,
                    "template_id": 213,
                    "segment_id": 189,
                    "name": "Take a look at a new feature",
                },
                "Email service not available: Unknown reason.",
            ),
            result,
        )
        self._job_repo.create_email_request.assert_awaited_once_with(
            189, 213, "Take a look at a new feature"
        )
        self._email_client.schedule_mailing_jobs.assert_awaited_once_with(
            self._jobs, "Click and see for yourself.", "Take a look at a new feature"
        )

    async def test_send_emails_unexpected_service_error(self):
        self._email_client.schedule_mailing_jobs.side_effect = UnexpectedServiceError(
            "No server"
        )

        result = await self.service.send_emails(
            189, 213, "Take a look at a new feature"
        )

        self.assertEqual(
            (
                {
                    "id": 42,
                    "template_id": 213,
                    "segment_id": 189,
                    "name": "Take a look at a new feature",
                },
                "Unexpected error occurred: No server.",
            ),
            result,
        )
        self._job_repo.create_email_request.assert_awaited_once_with(
            189, 213, "Take a look at a new feature"
        )
        self._email_client.schedule_mailing_jobs.assert_awaited_once_with(
            self._jobs, "Click and see for yourself.", "Take a look at a new feature"
        )

    async def test_get_email_requests(self):
        self._job_repo.get_email_requests.return_value = [
            {"id": 231, "name": "Hello!"},
            {"id": 231, "name": "Discounts"},
        ]

        result = await self.service.get_email_requests()

        self.assertEqual(
            [{"id": 231, "name": "Hello!"}, {"id": 231, "name": "Discounts"}], result
        )
        self._job_repo.get_email_requests.assert_awaited_once()

    async def test_get_email_request_details(self):
        self._job_repo.get_email_request.return_value = {
            "id": 231,
            "name": "Hello!",
            "template": {"id": 145, "name": "Welcome email"},
            "segment": {"id": 14, "name": "New users"},
        }
        self._job_repo.get_email_requests_job_statuses.return_value = [
            {
                "id": 45,
                "contact": {"id": 145, "name": "user1"},
                "status": EmailResult.FAILURE.value,
            },
            {
                "id": 46,
                "contact": {"id": 87, "name": "user2"},
                "status": EmailResult.SUCCESS.value,
            },
        ]

        result = await self.service.get_email_request_details(231)

        self.assertEqual(
            {
                "request": {
                    "id": 231,
                    "name": "Hello!",
                    "template": {"id": 145, "name": "Welcome email"},
                    "segment": {"id": 14, "name": "New users"},
                },
                "jobs": [
                    {
                        "id": 45,
                        "contact": {"id": 145, "name": "user1"},
                        "status": EmailResult.FAILURE.value,
                    },
                    {
                        "id": 46,
                        "contact": {"id": 87, "name": "user2"},
                        "status": EmailResult.SUCCESS.value,
                    },
                ],
            },
            result,
        )
        self._job_repo.get_email_request.assert_awaited_once_with(231)
        self._job_repo.get_email_requests_job_statuses.assert_awaited_once_with(231)

    async def test_update_job_statuses(self):
        statuses = {
            EmailResult.SUCCESS.value: [12, 14, 15],
            EmailResult.FAILURE.value: [16],
        }

        await self.service.update_jobs_statuses(statuses)

        self._job_repo.update_job_statuses.assert_awaited_once_with(statuses)
