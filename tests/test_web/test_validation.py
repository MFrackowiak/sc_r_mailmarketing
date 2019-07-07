from unittest import TestCase

from voluptuous import Invalid

from web.validation import validate_template


class TemplateValidateTestCase(TestCase):
    def test_validation_success(self):
        template = "Hey {name}! You agreed that we'll send spam to your email {email}."

        validate_template(template)

    def test_empty_param(self):
        template = "Hey {name}! You agreed that we'll send {} to your email {email}."

        self.assertRaises(Invalid, validate_template, template)

    def test_unsupported_param(self):
        template = "Hey {name}! You agree that we'll send stuff to your {12ds} {email}."

        self.assertRaises(Invalid, validate_template, template)
