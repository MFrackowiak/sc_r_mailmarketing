from asynctest import TestCase, CoroutineMock, MagicMock
from voluptuous import Invalid

from web.controllers.utils.errors import handle_errors


class TestHandleErrors(TestCase):
    def setUp(self):
        self._coro = CoroutineMock(__name__="Test coro")
        self.test_coro = handle_errors(self._coro)
        self._self = MagicMock()

    async def test_no_error(self):
        self._coro.return_value = "Test"

        self.assertEqual("Test", await self.test_coro(self._self, 1, 2))

        self._coro.assert_awaited_once_with(self._self, 1, 2)
        self._self.write.assert_not_called()
        self._self.loader.load.assert_not_called()

    async def test_validation_error(self):
        self._coro.side_effect = Invalid("Not an int")

        await self.test_coro(self._self, 1, 2)

        self._coro.assert_awaited_once_with(self._self, 1, 2)
        self._self.write.assert_called_once_with(
            self._self.loader.load.return_value.generate.return_value
        )
        self._self.loader.load.assert_called_once_with("error.html")
        self._self.loader.load.return_value.generate.assert_called_once_with(
            error="Not an int"
        )

    async def test_error(self):
        self._coro.side_effect = ValueError("Not an int")

        await self.test_coro(self._self, 1, 2)

        self._coro.assert_awaited_once_with(self._self, 1, 2)
        self._self.write.assert_called_once_with(
            self._self.loader.load.return_value.generate.return_value
        )
        self._self.loader.load.assert_called_once_with("error.html")
        self._self.loader.load.return_value.generate.assert_called_once_with()
