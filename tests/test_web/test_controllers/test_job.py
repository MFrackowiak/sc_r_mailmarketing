import json

from tests.test_web.test_controllers.base import BaseHandlerTest


class TestEmailHandler(BaseHandlerTest):
    def test_post(self):
        response = self.fetch(
            "/api/v1/job",
            method="POST",
            body=json.dumps(
                {
                    "success": [{"id": 1, "message_id": "<4370c0c3-c52f-42a0-9087-b73fd4ce149f@example.flypsdm.io>"}],
                    "retry": [{"id": 2, "message_id": ""}]
                }
            ),
        )
        self.assertEqual(response.code, 200)
        self.email_service.update_jobs_statuses.assert_awaited_once_with(
            {
                "success": [{"id": 1,
                             "message_id": "<4370c0c3-c52f-42a0-9087-b73fd4ce149f@example.flypsdm.io>"}],
                "retry": [{"id": 2, "message_id": ""}]
            }
        )
