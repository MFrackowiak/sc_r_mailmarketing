from typing import Optional

from tornado.template import Loader

from web.controllers.utils.errors import handle_errors
from web.controllers.utils.pagination import create_pagination_context
from web.controllers.utils.validated import ValidatedFormRequestHandler
from web.schemas import contact_schema, segment_contact_join_schema
from web.services.contact.abstract import AbstractContactService

DEFAULT_PER_PAGE = 25


class BaseContactRequestHandler(ValidatedFormRequestHandler):
    def initialize(
        self, template_loader: Loader, contact_service: AbstractContactService
    ):
        self.service = contact_service
        self.loader = template_loader


class ContactsHandler(BaseContactRequestHandler):
    schemas = {"post": contact_schema}

    @handle_errors
    async def get(self):
        page = self._get_page()
        contacts = await self.service.read_contacts(page, DEFAULT_PER_PAGE)
        pages = await self.service.get_contacts_pages_count(DEFAULT_PER_PAGE)

        pagination_context = create_pagination_context(page, pages)

        self.write(
            self.loader.load("contacts/contacts.html").generate(
                objects=contacts,
                columns=["id", "name", "email"],
                url_base="/contacts/",
                pages=pagination_context,
            )
        )

    @handle_errors
    async def post(self):
        data = self.get_data("post")
        contact = await self.service.create_contact(data)
        self.redirect(f"/contacts/{contact['id']}")


class ContactHandler(BaseContactRequestHandler):
    schemas = {"post": contact_schema}

    @handle_errors
    async def get(self, contact_id: str):
        contact = await self.service.get_contact(int(contact_id))
        self.write(self.loader.load("contacts/contact.html").generate(contact=contact))

    @handle_errors
    async def post(self, contact_id: str):
        data = self.get_data("post")
        data["id"] = int(contact_id)
        await self.service.update_contact(data)
        await self.get(contact_id)


class ContactFormHandler(BaseContactRequestHandler):
    @handle_errors
    async def get(self, contact_id: Optional[str] = None):
        if contact_id:
            action = f"/contacts/{contact_id}"
            initial = await self.service.get_contact(int(contact_id))
        else:
            action = "/contacts"
            initial = {}

        self.write(
            self.loader.load("contacts/contact_form.html").generate(
                action=action, initial=initial
            )
        )


class ContactSegmentFormHandler(BaseContactRequestHandler):
    schemas = {"post": segment_contact_join_schema}

    @handle_errors
    async def get(self, contact_id: str):
        action = f"/contacts/{contact_id}/segments"
        segments = await self.service.read_segments(
            0, DEFAULT_PER_PAGE
        )  # TODO all contact can join

        self.write(
            self.loader.load("contacts/contact_segment_form.html").generate(
                action=action, segments=segments
            )
        )

    @handle_errors
    async def post(self, contact_id: str):
        data = self.get_data("post")
        await self.service.add_contact_to_segment(data["segment_id"], int(contact_id))
        self.redirect(f"/contacts/{contact_id}")
