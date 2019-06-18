from asynctest import (
    TestCase,
    create_autospec,
    MagicMock,
    patch,
    CoroutineMock,
    call,
    Mock,
)

from email_client.integrations.email.abstract import (
    AbstractEmailGatewayClient,
    EmailResult,
)
from email_client.integrations.web.abstract import AbstractWebClient
from email_client.services.email.service import SendEmailService
from email_client.settings.abstract import AbstractSettingsStorage


class SendEmailServiceTestCase(TestCase):
    def setUp(self):
        self.web_client = create_autospec(AbstractWebClient)
        self.email_client = create_autospec(AbstractEmailGatewayClient)
        self.settings_storage = create_autospec(AbstractSettingsStorage)

        self.ensure_future_patch = patch(
            "email_client.services.email.service.ensure_future"
        )
        self.ensure_future_mock = self.ensure_future_patch.start()

    def tearDown(self):
        self.ensure_future_patch.stop()

    def test_dispatch_sending_emails(self):
        service = SendEmailService(
            self.web_client, self.email_client, self.settings_storage, 2
        )

        with patch.object(service, "send_emails", MagicMock()) as send_emails:
            service.dispatch_sending_emails(
                [
                    {"id": i, "email": f"guy_{i}@co.co", "name": "Guy"}
                    for i in range(1, 6)
                ],
                "Hi {name}! Have a nice day",
            )
            send_emails.assert_called_once_with(
                [
                    {"id": i, "email": f"guy_{i}@co.co", "name": "Guy"}
                    for i in range(1, 6)
                ],
                "Hi {name}! Have a nice day",
            )
            self.ensure_future_mock.assert_called_once_with(send_emails.return_value)

    async def test_send_emails_no_retry(self):
        params = (
            ("user", "pass"),
            {"reply-to": "spam@co.co"},
            {"name": "Admin", "email": "admin@co.co"},
        )
        self.settings_storage.get_gateway_credentials_headers_and_from.return_value = (
            params
        )
        send_email_batch_mock = CoroutineMock(return_value=[])

        service = SendEmailService(
            self.web_client, self.email_client, self.settings_storage, 2
        )

        with patch.object(service, "send_email_batch", send_email_batch_mock):
            await service.send_emails(
                [
                    {"id": i, "email": f"guy_{i}@co.co", "name": "Guy"}
                    for i in range(1, 6)
                ],
                "Hi {name}! Have a nice day",
            )

        self.settings_storage.get_gateway_credentials_headers_and_from.assert_awaited_once()
        send_email_batch_mock.assert_has_calls(
            [
                call(
                    [
                        {"id": 1, "email": "guy_1@co.co", "name": "Guy"},
                        {"id": 2, "email": "guy_2@co.co", "name": "Guy"},
                    ],
                    "Hi {name}! Have a nice day",
                    *params,
                ),
                call(
                    [
                        {"id": 3, "email": "guy_3@co.co", "name": "Guy"},
                        {"id": 4, "email": "guy_4@co.co", "name": "Guy"},
                    ],
                    "Hi {name}! Have a nice day",
                    *params,
                ),
                call(
                    [{"id": 5, "email": "guy_5@co.co", "name": "Guy"}],
                    "Hi {name}! Have a nice day",
                    *params,
                ),
            ]
        )
        self.ensure_future_mock.assert_not_called()

    async def test_send_emails_with_retry(self):
        params = (
            ("user", "pass"),
            {"reply-to": "spam@co.co"},
            {"name": "Admin", "email": "admin@co.co"},
        )
        self.settings_storage.get_gateway_credentials_headers_and_from.return_value = (
            params
        )
        send_email_batch_mock = CoroutineMock(
            side_effect=[
                [],
                [
                    {"id": 3, "email": "guy_3@co.co", "name": "Guy"},
                    {"id": 4, "email": "guy_4@co.co", "name": "Guy"},
                ],
                [],
            ]
        )
        manage_retry_mock = Mock()

        service = SendEmailService(
            self.web_client, self.email_client, self.settings_storage, 2
        )

        with patch.object(
            service, "send_email_batch", send_email_batch_mock
        ), patch.object(service, "manage_retry", manage_retry_mock):
            await service.send_emails(
                [
                    {"id": i, "email": f"guy_{i}@co.co", "name": "Guy"}
                    for i in range(1, 6)
                ],
                "Hi {name}! Have a nice day",
            )

        self.settings_storage.get_gateway_credentials_headers_and_from.assert_awaited_once()
        send_email_batch_mock.assert_has_calls(
            [
                call(
                    [
                        {"id": 1, "email": "guy_1@co.co", "name": "Guy"},
                        {"id": 2, "email": "guy_2@co.co", "name": "Guy"},
                    ],
                    "Hi {name}! Have a nice day",
                    *params,
                ),
                call(
                    [
                        {"id": 3, "email": "guy_3@co.co", "name": "Guy"},
                        {"id": 4, "email": "guy_4@co.co", "name": "Guy"},
                    ],
                    "Hi {name}! Have a nice day",
                    *params,
                ),
                call(
                    [{"id": 5, "email": "guy_5@co.co", "name": "Guy"}],
                    "Hi {name}! Have a nice day",
                    *params,
                ),
            ]
        )
        manage_retry_mock.assert_called_once_with(
            [
                {"id": 3, "email": "guy_3@co.co", "name": "Guy"},
                {"id": 4, "email": "guy_4@co.co", "name": "Guy"},
            ],
            "Hi {name}! Have a nice day",
            1,
        )
        self.ensure_future_mock.assert_called_once_with(manage_retry_mock.return_value)

    @patch("email_client.services.email.service.sleep", new_callable=CoroutineMock)
    async def test_manage_retry(self, sleep_mock: CoroutineMock):
        send_emails_mock = CoroutineMock()

        service = SendEmailService(
            self.web_client, self.email_client, self.settings_storage, 10, 3, 2
        )

        with patch.object(service, "send_emails", send_emails_mock):
            await service.manage_retry(
                [
                    {"id": 3, "email": "guy_3@co.co", "name": "Guy"},
                    {"id": 4, "email": "guy_4@co.co", "name": "Guy"},
                ],
                "Hi {name}! Have a nice day",
                3,
            )

        sleep_mock.assert_awaited_once_with(8)
        send_emails_mock.assert_awaited_once_with(
            [
                {"id": 3, "email": "guy_3@co.co", "name": "Guy"},
                {"id": 4, "email": "guy_4@co.co", "name": "Guy"},
            ],
            "Hi {name}! Have a nice day",
            3,
        )

    @patch("email_client.services.email.service.sleep", new_callable=CoroutineMock)
    async def test_manage_retry_limit_reached(self, sleep_mock: CoroutineMock):
        send_emails_mock = CoroutineMock()

        service = SendEmailService(
            self.web_client, self.email_client, self.settings_storage, 10, 3, 2
        )

        with patch.object(service, "send_emails", send_emails_mock):
            await service.manage_retry(
                [
                    {"id": 3, "email": "guy_3@co.co", "name": "Guy"},
                    {"id": 4, "email": "guy_4@co.co", "name": "Guy"},
                ],
                "Hi {name}! Have a nice day",
                4,
            )

        sleep_mock.assert_not_awaited()
        send_emails_mock.assert_not_awaited()
        self.web_client.report_job_status.assert_awaited_once_with(
            {EmailResult.FAILURE: [3, 4]}
        )

    async def test_send_email_batch(self):
        self.email_client.send_emails.return_value = (
            {EmailResult.AUTH_FAILURE: [1], EmailResult.SUCCESS: [2, 3]},
            [{"id": 4, "email": "guy_4@co.co", "name": "Guy"}],
        )

        service = SendEmailService(
            self.web_client, self.email_client, self.settings_storage, 4, 3, 2
        )

        self.assertEqual(
            await service.send_email_batch(
                [
                    {"id": i, "email": f"guy_{i}@co.co", "name": "Guy"}
                    for i in range(1, 5)
                ],
                "Hi {name}! Have a nice day",
                ("user", "pass"),
                {"reply-to": "spam@co.co"},
                {"name": "Admin", "email": "admin@co.co"},
            ),
            [{"id": 4, "email": "guy_4@co.co", "name": "Guy"}],
        )

        self.email_client.send_emails.assert_awaited_once_with(
            [{"id": i, "email": f"guy_{i}@co.co", "name": "Guy"} for i in range(1, 5)],
            "Hi {name}! Have a nice day",
            ("user", "pass"),
            {"name": "Admin", "email": "admin@co.co"},
            {"reply-to": "spam@co.co"},
        )
        self.web_client.report_job_status.assert_awaited_once_with(
            {EmailResult.AUTH_FAILURE: [1], EmailResult.SUCCESS: [2, 3]}
        )
