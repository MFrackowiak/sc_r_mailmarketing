from http import HTTPStatus

from tornado.template import Loader

from web.controllers.utils.errors import handle_errors
from web.controllers.utils.validated import ValidatedFormRequestHandler
from web.schemas import settings_schema
from web.services.settings.abstract import AbstractSettingsService


class SettingsRequestHandler(ValidatedFormRequestHandler):
    schemas = {"post": settings_schema}

    def initialize(
        self, template_loader: Loader, settings_service: AbstractSettingsService
    ):
        self.loader = template_loader
        self.service = settings_service

    @handle_errors
    async def get(self):
        success, value = await self.service.get_current_settings()

        if success:
            self.write(self.loader.load("settings/form.html").generate(initial=value))
        else:
            self.set_status(HTTPStatus.INTERNAL_SERVER_ERROR)
            self.write(self.loader.load("error.html").generate(error=value))

    @handle_errors
    async def post(self):
        data = self.get_data("post")

        success, error = await self.service.update_settings(data)

        if success:
            await self.get()
        else:
            self.set_status(HTTPStatus.INTERNAL_SERVER_ERROR)
            self.write(self.loader.load("error.html").generate(error=error))
