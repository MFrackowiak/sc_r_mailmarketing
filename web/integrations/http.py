from aiohttp.web_response import Response

from common.exceptions import (
    ValidationError,
    UnavailableServiceError,
    UnexpectedServiceError,
)


class BaseHTTPClient:
    @classmethod
    async def _raise_for_code(cls, response: Response):
        try:
            data = await response.json()
            error = data["error"]
        except (TypeError, AttributeError, KeyError):
            error = "Unknown error"

        if response.code == 400:
            raise ValidationError(error)
        elif response.code in {502, 503}:
            raise UnavailableServiceError(error)
        else:
            raise UnexpectedServiceError(error)
