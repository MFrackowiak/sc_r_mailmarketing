from asynctest import TestCase, Mock, CoroutineMock
from voluptuous import Coerce, Email, Schema

from common.decorators import validate_json, handle_errors
from common.exceptions import ValidationError, UnsupportedFormatError


class TestValidateDecoratorTestCase(TestCase):
    def setUp(self):
        self.dummy_func = Mock()
        self.self_dummy = Mock(
            request=Mock(),
            _schemas={
                "post": Schema(
                    {"job_id": Coerce(int), "email": Email(), "template": str}
                )
            },
        )

    def test_validation_passed(self):
        self.self_dummy.request.method = "POST"
        self.self_dummy.request.body = (
            b'{"job_id": 12, "email": "random@guy.co", "template": "Hello!"}'
        )

        validate_json(self.dummy_func)(self.self_dummy)

        self.dummy_func.assert_called_once_with(
            self.self_dummy,
            {"job_id": 12, "email": "random@guy.co", "template": "Hello!"},
        )

    def test_validation_invalid(self):
        self.self_dummy.request.method = "POST"
        self.self_dummy.request.body = (
            b'{"job_id": "test", "email": "random@guy.co", "template": "Hello!"}'
        )

        with self.assertRaises(ValidationError):
            validate_json(self.dummy_func)(self.self_dummy)

        self.dummy_func.assert_not_called()

    def test_schema_not_found(self):
        self.self_dummy.request.method = "PUT"
        self.self_dummy.request.body = (
            b'{"job_id": 12, "email": "random@guy.co", "template": "Hello!"}'
        )

        with self.assertRaises(ValidationError):
            validate_json(self.dummy_func)(self.self_dummy)

        self.dummy_func.assert_not_called()

    def test_invalid_json(self):
        self.self_dummy.request.method = "POST"
        self.self_dummy.request.body = b"Hello"

        with self.assertRaises(UnsupportedFormatError):
            validate_json(self.dummy_func)(self.self_dummy)

        self.dummy_func.assert_not_called()


class TestHandleErrorsDecoratorTestCase(TestCase):
    def setUp(self):
        self.dummy_coro = CoroutineMock(__name__="coro")
        self.handler_mock = Mock(set_status=Mock(), write=Mock())

    async def test_no_errors(self):
        await handle_errors(self.dummy_coro)(self.handler_mock)

        self.dummy_coro.assert_awaited_once_with(self.handler_mock)
        self.handler_mock.set_status.assert_not_called()
        self.handler_mock.write.assert_not_called()

    async def test_validation_error(self):
        self.dummy_coro.side_effect = ValidationError("Expected str not int")

        await handle_errors(self.dummy_coro)(self.handler_mock)

        self.dummy_coro.assert_awaited_once_with(self.handler_mock)
        self.handler_mock.set_status.assert_called_once_with(400)
        self.handler_mock.write.assert_called_once_with(
            {"error": "Expected str not int"}
        )

    async def test_unsupported_format(self):
        self.dummy_coro.side_effect = UnsupportedFormatError("Expected JSON")

        await handle_errors(self.dummy_coro)(self.handler_mock)

        self.dummy_coro.assert_awaited_once_with(self.handler_mock)
        self.handler_mock.set_status.assert_called_once_with(415)
        self.handler_mock.write.assert_called_once_with({"error": "Expected JSON"})

    async def test_server_error(self):
        self.dummy_coro.side_effect = ValueError("It didn't work")

        await handle_errors(self.dummy_coro)(self.handler_mock)

        self.dummy_coro.assert_awaited_once_with(self.handler_mock)
        self.handler_mock.set_status.assert_called_once_with(500)
        self.handler_mock.write.assert_called_once_with({"error": "It didn't work"})
