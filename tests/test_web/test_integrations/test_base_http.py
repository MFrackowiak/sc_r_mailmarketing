from asynctest import TestCase, CoroutineMock, Mock

from common.exceptions import (
    ValidationError,
    UnavailableServiceError,
    UnexpectedServiceError,
)
from web.integrations.http import BaseHTTPClient


class TestBaseHTTPClient(TestCase):
    async def test_bad_request(self):
        response = Mock(
            code=400,
            json=CoroutineMock(return_value={"error": "Missing required_data"}),
        )

        with self.assertRaises(ValidationError) as exc_dec:
            await BaseHTTPClient._raise_for_code(response)

        self.assertEqual(exc_dec.exception.args, ("Missing required_data",))

    async def test_bad_gateway(self):
        response = Mock(code=502, json=CoroutineMock(return_value={"status": "Down"}))

        with self.assertRaises(UnavailableServiceError) as exc_dec:
            await BaseHTTPClient._raise_for_code(response)

        self.assertEqual(exc_dec.exception.args, ("Unknown error",))

    async def test_service_unavailable(self):
        response = Mock(code=503, json=CoroutineMock(side_effect=AttributeError()))

        with self.assertRaises(UnavailableServiceError) as exc_dec:
            await BaseHTTPClient._raise_for_code(response)

        self.assertEqual(exc_dec.exception.args, ("Unknown error",))

    async def test_internal_server_error(self):
        response = Mock(
            code=500, json=CoroutineMock(return_value={"error": "Server exploded"})
        )

        with self.assertRaises(UnexpectedServiceError) as exc_dec:
            await BaseHTTPClient._raise_for_code(response)

        self.assertEqual(exc_dec.exception.args, ("Server exploded",))
