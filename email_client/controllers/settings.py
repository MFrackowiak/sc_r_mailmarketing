from http import HTTPStatus
from typing import Dict

from tornado.web import RequestHandler

from common.decorators import handle_errors, validate
from email_client.schemas import settings_schema
from email_client.services.settings.abstract import AbstractSettingsService


class SettingsHandler(RequestHandler):
    _schemas = {"patch": settings_schema}

    def initialize(self, settings_service: AbstractSettingsService):
        self.service = settings_service

    @handle_errors
    async def get(self):
        data = await self.service.get_custom_headers_and_email_from()
        self.set_status(HTTPStatus.OK)
        self.write(data)

    @handle_errors
    @validate
    async def patch(self, data: Dict):
        if "auth" in data:
            await self.service.update_email_credentials(**data["auth"])
        if "email_from" in data:
            await self.service.update_email_from(**data["email_from"])
        if "headers" in data:
            await self.service.update_custom_headers(headers=data["headers"])

        if data:
            self.set_status(HTTPStatus.OK)
        else:
            self.set_status(HTTPStatus.NO_CONTENT)
