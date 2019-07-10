from asyncio import ensure_future
from http import HTTPStatus

from tornado.web import RequestHandler

from common.decorators import handle_errors, validate_json
from email_client.schemas import job_request_schema
from email_client.services.email.abstract import AbstractSendEmailService


class EmailHandler(RequestHandler):
    _schemas = {"post": job_request_schema}

    def initialize(self, email_service: AbstractSendEmailService):
        self.service = email_service

    @handle_errors
    @validate_json
    async def post(self, data):
        ensure_future(self.service.send_emails(**data))
        self.set_status(HTTPStatus.ACCEPTED)
