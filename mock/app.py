from base64 import b64decode
from http import HTTPStatus
from itertools import cycle
from random import choices
from uuid import uuid4

from tornado import escape
from tornado.web import RequestHandler, Application

statuses = cycle(
    choices(
        [
            HTTPStatus.ACCEPTED,
            HTTPStatus.INTERNAL_SERVER_ERROR,
            HTTPStatus.BAD_GATEWAY,
            HTTPStatus.BAD_REQUEST,
            HTTPStatus.UNAUTHORIZED,
            HTTPStatus.FORBIDDEN,
        ],
        [70, 20, 3, 3, 2, 2],
        k=1000,
    )
)


class EmailRequestHandler(RequestHandler):
    def post(self):
        print(escape.json_decode(self.request.body))
        auth_header = self.request.headers.get_list("Authorization")[0]
        print(self._decode_auth(auth_header))
        status = next(statuses)
        self.set_status(status)

        if status == HTTPStatus.ACCEPTED:
            self.write({"message_id": str(uuid4())})

    def _decode_auth(self, content):
        split = content.strip().split(" ")

        username, password = b64decode(split[1]).decode().split(":")

        return username, password


def init_app():
    return Application([(r"/email", EmailRequestHandler)])
