from unittest import TestCase

from voluptuous import Invalid

from web.schemas import settings_schema


class TestSettingsSchema(TestCase):
    def test_only_one_group(self):
        data = {"name": "some guy", "email": "some@guy.com"}
        self.assertEqual(data, settings_schema(data))

        data = {"user": "sdk12314", "password": "admin1"}
        self.assertEqual(data, settings_schema(data))

    def test_missing_from_one_group(self):
        data = {"name": "some guy"}
        self.assertRaises(Invalid, settings_schema, data)

    def test_missing_from_both_groups(self):
        data = {"name": "some guy", "user": "some@guy.com"}
        self.assertRaises(Invalid, settings_schema, data)
