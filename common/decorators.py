import traceback
from functools import wraps
from http import HTTPStatus
from json import JSONDecodeError
from logging import getLogger
from typing import Callable

from tornado import escape
from voluptuous import Invalid

from common.exceptions import (
    UnsupportedFormatError,
    ValidationError,
    UnavailableServiceError,
)

logger = getLogger(__name__)


def validate_json(func: Callable):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            http_method = self.request.method.lower()

            data = escape.json_decode(self.request.body)

            validated_data = self._schemas[http_method](data)
        except Invalid as e:
            raise ValidationError(e.error_message)
        except (AttributeError, KeyError, TypeError) as e:
            raise ValidationError(
                "Failed validation for {self.__class__.__name__}.{func.__name__}"
            ) from e
        except (TypeError, JSONDecodeError) as e:
            raise UnsupportedFormatError(repr(e))
        return func(self, validated_data, *args, **kwargs)

    return wrapper


def catch_timeout(func: Callable):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except TimeoutError:
            return UnavailableServiceError(
                "Couldn't finish operation - connection timed out."
            )

    return wrapper


def handle_errors(func: Callable):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        try:
            await func(self, *args, **kwargs)
        except ValidationError as e:
            self.set_status(HTTPStatus.BAD_REQUEST)
            self.write({"error": str(e)})
        except UnsupportedFormatError as e:
            self.set_status(HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
            self.write({"error": str(e)})
        except Exception as e:
            logger.error(
                f"Encounctered an error when processing request - {self.__class__.__name__}.{func.__name__}: {traceback.format_exc()}"
            )
            self.set_status(HTTPStatus.INTERNAL_SERVER_ERROR)
            self.write({"error": str(e)})

    return wrapper
