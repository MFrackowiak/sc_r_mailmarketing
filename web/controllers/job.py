from typing import Dict

from tornado.web import RequestHandler

from common.decorators import handle_errors, validate_json
from web.schemas import update_status_schema
from web.services.email.abstract import AbstractEmailService


class JobStatusHandler(RequestHandler):
    _schemas = {"post": update_status_schema}

    def initialize(self, email_service: AbstractEmailService):
        self.service = email_service

    @handle_errors
    @validate_json
    async def post(self, data: Dict):
        await self.service.update_jobs_statuses(data)
        self.set_status(200)
        self.finish()
