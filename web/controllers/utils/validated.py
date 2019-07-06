from typing import Dict

from tornado.web import RequestHandler
from voluptuous import Schema


class ValidatedFormRequestHandler(RequestHandler):
    schemas: Dict[str, Schema] = {}

    def get_data(self, request_method: str):
        schema = self.schemas[request_method]

        arg_getter = (
            self.get_body_argument
            if request_method == "post"
            else self.get_query_argument
        )

        data = {key: arg_getter(key) for key in schema.schema.keys()}

        if not data:
            return None

        return schema(data)
