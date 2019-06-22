from unittest import TestCase

from voluptuous import Invalid

from email_client.schemas import job_schema, job_request_schema, settings_schema


class EmailClientSchemasTestCase(TestCase):
    def test_job_schema_keys_required(self):
        test_dict = {"id": 12, "subject": "None"}
        self.assertRaises(Invalid, job_schema, test_dict)

    def test_job_schema_name_optional(self):
        test_dict = {"id": 12, "subject": "None", "email": "guy@co.co"}
        self.assertEqual(job_schema(test_dict), test_dict)

    def test_job_schema_extra_allowed(self):
        test_dict = {
            "id": 12,
            "subject": "None",
            "email": "guy@co.co",
            "name": "Guy",
            "first_name": "Guy",
            "last_name": "",
            "user_id": 145,
        }
        self.assertEqual(job_schema(test_dict), test_dict)

    def test_job_request_schema(self):
        test_dict = {
            "jobs": [
                {"id": 13, "subject": "None", "email": "guy@co.co"},
                {"id": 14, "subject": "None", "email": "other@co.co"},
            ],
            "template": "Hello!",
        }
        self.assertEqual(job_request_schema(test_dict), test_dict)

    def test_job_request_schema_at_least_one_job(self):
        test_dict = {"jobs": [], "template": "Hello!"}
        self.assertRaises(Invalid, job_request_schema, test_dict)

    def test_job_request_schema_extra_not_allowed(self):
        test_dict = {
            "jobs": [
                {"id": 13, "subject": "None", "email": "guy@co.co"},
                {"id": 14, "subject": "None", "email": "other@co.co"},
            ],
            "template": "Hello!",
            "extra": True,
        }
        self.assertRaises(Invalid, job_request_schema, test_dict)

    def test_settings_schema_not_all_required(self):
        test_dict = {"auth": {"user": "admin", "password": "admin1"}}
        self.assertEqual(settings_schema(test_dict), test_dict)
