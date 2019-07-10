from typing import Dict

from tornado.web import RequestHandler
from voluptuous import Schema


class ValidatedFormRequestHandler(RequestHandler):
    schemas: Dict[str, Schema] = {}

    def get_data(self, request_method: str):
        schema = self.schemas[request_method]

        data = {
            key: self.get_body_argument(key)
            for key in self.request.body_arguments.keys()
        }

        if not data:
            return None

        return schema(data)

    def _get_page(self) -> int:
        page = int(self.get_query_argument("page", "1"))

        if page < 1:
            page = 1

        return page
