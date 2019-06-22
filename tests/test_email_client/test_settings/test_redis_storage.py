from asynctest import TestCase, CoroutineMock, Mock

from email_client.settings.redis import SimpleRedisSettingsStorage


class SimpleRedisSettingsStorageTestCase(TestCase):
    def setUp(self):
        self.redis = Mock(
            hmget=CoroutineMock(),
            hgetall=CoroutineMock(),
            hmset=CoroutineMock(),
            delete=CoroutineMock(),
        )
        self.storage = SimpleRedisSettingsStorage(self.redis)

    async def test_get_custom_headers(self):
        self.redis.hgetall.return_value = [
            "reply-to",
            "Admin <admin@co.co>",
            "x-tracing",
            "35adc1235",
        ]
        self.assertEqual(
            await self.storage.get_custom_headers(),
            {"reply-to": "Admin <admin@co.co>", "x-tracing": "35adc1235"},
        )
        self.redis.hgetall.assert_awaited_once_with(
            "email_client/settings/headers", encoding="utf8"
        )

    async def test_save_custom_headers(self):
        await self.storage.save_custom_headers(
            {"reply-to": "Admin <admin@co.co>", "x-tracing": "35adc1235"}
        )
        self.redis.delete.assert_awaited_once_with("email_client/settings/headers")
        self.redis.hmset.assert_awaited_once_with(
            "email_client/settings/headers",
            "reply-to",
            "Admin <admin@co.co>",
            "x-tracing",
            "35adc1235",
        )

    async def test_get_email_from(self):
        self.redis.hmget.return_value = ["Admin", "admin@co.co"]
        self.assertEqual(
            await self.storage.get_email_from(),
            {"name": "Admin", "email": "admin@co.co"},
        )
        self.redis.hmget.assert_awaited_once_with(
            "email_client/settings/email_from", "name", "email", encoding="utf8"
        )

    async def test_save_email_from(self):
        await self.storage.save_email_from("Admin", "admin@co.co")
        self.redis.hmset.assert_awaited_once_with(
            "email_client/settings/email_from",
            "name",
            b"Admin",
            "email",
            b"admin@co.co",
        )

    async def test_save_gateway_credentials(self):
        await self.storage.save_gateway_credentials("user1", "admin1")
        self.redis.hmset.assert_awaited_once_with(
            "email_client/settings/auth", "username", b"user1", "password", b"admin1"
        )

    async def test_get_gateway_credentials(self):
        self.redis.hmget.return_value = ["user", "admin1"]
        self.assertEqual(
            await self.storage.get_gateway_credentials(), ("user", "admin1")
        )
        self.redis.hmget.assert_awaited_once_with(
            "email_client/settings/auth", "username", "password", encoding="utf8"
        )

    async def test_get_gateway_credentials_headers_and_from(self):
        self.redis.hmget.side_effect = [["user", "admin1"], ["Admin", "admin@co.co"]]
        self.redis.hgetall.return_value = []
        self.assertEqual(
            await self.storage.get_gateway_credentials_headers_and_from(),
            (("user", "admin1"), {}, {"name": "Admin", "email": "admin@co.co"}),
        )
