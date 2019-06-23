from asynctest import TestCase, Mock, CoroutineMock, patch, call

from common.enums import EmailResult
from email_client.integrations.web.client import WebClient


class WebClientTestCase(TestCase):
    def setUp(self):
        self.session = Mock(post=CoroutineMock())
        self.logger_patch = patch("email_client.integrations.web.client.logger")
        self.logger_mock = self.logger_patch.start()

    def tearDown(self):
        self.logger_patch.stop()

    async def test_report_job_statuses(self):
        self.session.post.return_value = Mock(status=200)
        job_updates = {
            EmailResult.SUCCESS: [{"id": 142, "message_id": "df431-ac221"}],
            EmailResult.FAILURE: [42, 49],
        }

        client = WebClient("http://service", self.session)

        await client.report_job_status(job_updates)

        self.session.post.assert_awaited_once_with(
            "http://service",
            json={
                "success": [{"id": 142, "message_id": "df431-ac221"}],
                "failure": [42, 49],
            },
        )
        self.logger_mock.warning.assert_not_called()
        self.logger_mock.error.assert_not_called()
        self.logger_mock.critical.assert_not_called()

    @patch("email_client.integrations.web.client.sleep", new_callable=CoroutineMock)
    async def test_report_job_statuses_retry(self, sleep_mock: CoroutineMock):
        self.session.post.side_effect = [
            ConnectionError(),
            Mock(status=502),
            ValueError(),
            Mock(status=200),
        ]
        job_updates = {
            EmailResult.SUCCESS: [{"id": 142, "message_id": "df431-ac221"}],
            EmailResult.FAILURE: [42, 49],
        }

        client = WebClient("http://service", self.session)

        await client.report_job_status(job_updates)

        self.session.post.assert_has_awaits(
            [
                call(
                    "http://service",
                    json={
                        "success": [{"id": 142, "message_id": "df431-ac221"}],
                        "failure": [42, 49],
                    },
                )
            ]
            * 4
        )

        sleep_mock.assert_has_awaits([call(3), call(9), call(27)])

        self.logger_mock.warning.assert_called()
        self.logger_mock.error.assert_called()
        self.logger_mock.critical.assert_not_called()

    @patch("email_client.integrations.web.client.sleep", new_callable=CoroutineMock)
    async def test_report_job_statuses_failure(self, sleep_mock: CoroutineMock):
        self.session.post.side_effect = [
            ConnectionError(),
            Mock(status=502),
            ValueError(),
            Mock(status=400),
        ]
        job_updates = {
            EmailResult.SUCCESS: [{"id": 142, "message_id": "df431-ac221"}],
            EmailResult.FAILURE: [42, 49],
        }

        client = WebClient("http://service", self.session)

        await client.report_job_status(job_updates)

        self.session.post.assert_has_awaits(
            [
                call(
                    "http://service",
                    json={
                        "success": [{"id": 142, "message_id": "df431-ac221"}],
                        "failure": [42, 49],
                    },
                )
            ]
            * 4
        )

        sleep_mock.assert_has_awaits([call(3), call(9), call(27)])

        self.logger_mock.warning.assert_called()
        self.logger_mock.error.assert_called()
        self.logger_mock.critical.assert_called()
