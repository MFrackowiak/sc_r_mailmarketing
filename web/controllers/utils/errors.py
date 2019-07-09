import logging
import traceback
from functools import wraps
from http import HTTPStatus
from typing import Callable

from voluptuous import Invalid


def handle_errors(func: Callable):
    @wraps(func)
    async def handle_template_errors(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except Invalid as e:
            logging.info(
                f"Validation error occured when handling {self.__class__.__name__}.{func.__name__}: {traceback.format_exc()}"
            )
            self.set_status(HTTPStatus.BAD_REQUEST)
            self.write(self.loader.load("error.html").generate(error=str(e)))
        except Exception:
            logging.error(
                f"Error occured when handling {self.__class__.__name__}.{func.__name__}: {traceback.format_exc()}"
            )
            self.set_status(HTTPStatus.INTERNAL_SERVER_ERROR)
            self.write(self.loader.load("error.html").generate())

    return handle_template_errors
