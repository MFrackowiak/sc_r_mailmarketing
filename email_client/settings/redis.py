from asyncio import gather
from itertools import chain
from typing import Tuple, Dict

from aioredis import Redis

from email_client.settings.abstract import AbstractSettingsStorage


class SimpleRedisSettingsStorage(AbstractSettingsStorage):
    base_key = "email_client/settings"

    def __init__(self, connection: Redis):
        self._connection = connection

    def get_key(self, key: str):
        return f"{self.base_key}/{key}"

    async def save_custom_headers(self, headers: Dict):
        key = self.get_key("headers")
        await self._connection.delete(key)
        await self._connection.hmset(key, *chain(*headers.items()))

    async def get_custom_headers(self) -> Dict:
        headers_list = await self._connection.hgetall(
            self.get_key("headers"), encoding="utf8"
        )
        return headers_list

    async def get_email_from(self) -> Dict[str, str]:
        name, email = await self._connection.hmget(
            self.get_key("email_from"), "name", "email", encoding="utf8"
        )
        return {"name": name, "email": email}

    async def save_email_from(self, name: str, email: str):
        await self._connection.hmset(
            self.get_key("email_from"),
            "name",
            name.encode("utf8"),
            "email",
            email.encode("utf8"),
        )

    async def save_gateway_credentials(self, username: str, password: str):
        await self._connection.hmset(
            self.get_key("auth"),
            "username",
            username.encode("utf8"),
            "password",
            password.encode("utf8"),
        )

    async def get_gateway_credentials(self) -> Tuple[str, str]:
        username, password = await self._connection.hmget(
            self.get_key("auth"), "username", "password", encoding="utf8"
        )
        return username, password

    async def get_gateway_credentials_headers_and_from(
        self
    ) -> Tuple[Tuple[str, str], Dict, Dict[str, str]]:
        return tuple(
            await gather(
                *[
                    self.get_gateway_credentials(),
                    self.get_custom_headers(),
                    self.get_email_from(),
                ]
            )
        )
