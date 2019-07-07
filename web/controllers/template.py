from typing import Optional

from tornado.template import Loader

from web.controllers.utils.errors import handle_errors
from web.controllers.utils.validated import ValidatedFormRequestHandler
from web.schemas import template_schema
from web.services.email.abstract import AbstractEmailService
from web.validation import validate_template_schema


class BaseTemplateRequestHandler(ValidatedFormRequestHandler):
    def initialize(self, template_loader: Loader, email_service: AbstractEmailService):
        self.service = email_service
        self.loader = template_loader


class TemplatesHandler(BaseTemplateRequestHandler):
    schemas = {"post": template_schema}

    @handle_errors
    async def get(self):
        contacts = await self.service.list_email_templates()
        self.write(
            self.loader.load("templates/templates.html").generate(
                objects=contacts, columns=["id", "name"], url_base="/templates/"
            )
        )

    @handle_errors
    async def post(self):
        data = self.get_data("post")
        validate_template_schema(data)
        template = await self.service.create_email_template(data)
        self.redirect(f"/templates/{template['id']}")


class TemplateHandler(BaseTemplateRequestHandler):
    schemas = {"post": template_schema}

    @handle_errors
    async def get(self, template_id: str):
        template = await self.service.get_email_template(int(template_id))
        self.write(
            self.loader.load("templates/template.html").generate(template=template)
        )

    @handle_errors
    async def post(self, template_id: str):
        data = self.get_data("post")
        validate_template_schema(data)
        data["id"] = int(template_id)

        await self.service.update_email_template(data)
        await self.get(template_id)


class TemplateFormHandler(BaseTemplateRequestHandler):
    @handle_errors
    async def get(self, template_id: Optional[str] = None):
        if template_id:
            action = f"/templates/{template_id}"
            initial = await self.service.get_email_template(int(template_id))
        else:
            action = "/templates"
            initial = {}

        self.write(
            self.loader.load("templates/template_form.html").generate(
                action=action, initial=initial
            )
        )
