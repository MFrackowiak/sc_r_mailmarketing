import logging
import traceback
from functools import wraps
from typing import Callable


def handle_errors(func: Callable):
    @wraps(func)
    async def handle_template_errors(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except Exception:
            logging.error(
                f"Error occured when handling {self.__class__.__name__}.{func.__name__}: {traceback.format_exc()}"
            )
            self.write(self.loader.load("error.html").generate())

    return handle_template_errors
