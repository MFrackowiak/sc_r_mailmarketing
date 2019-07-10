from typing import Optional

from tornado.template import Loader

from web.controllers.utils.errors import handle_errors
from web.controllers.utils.pagination import create_pagination_context
from web.controllers.utils.validated import ValidatedFormRequestHandler
from web.schemas import segment_schema
from web.services.contact.abstract import AbstractContactService

DEFAULT_PER_PAGE = 25


class BaseSegmentRequestHandler(ValidatedFormRequestHandler):
    def initialize(
        self, template_loader: Loader, contact_service: AbstractContactService
    ):
        self.service = contact_service
        self.loader = template_loader


class SegmentsHandler(BaseSegmentRequestHandler):
    schemas = {"post": segment_schema}

    @handle_errors
    async def get(self):
        page = self._get_page()
        contacts = await self.service.read_segments(int(page), DEFAULT_PER_PAGE)
        pages = await self.service.get_segments_pages_count(DEFAULT_PER_PAGE)

        pagination_context = create_pagination_context(page, pages)

        self.write(
            self.loader.load("segments/segments.html").generate(
                objects=contacts,
                columns=["id", "name"],
                url_base="/segments/",
                pages=pagination_context,
            )
        )

    @handle_errors
    async def post(self):
        data = self.get_data("post")
        segment = await self.service.create_segment(data)
        self.redirect(f"/segments/{segment['id']}")


class SegmentHandler(BaseSegmentRequestHandler):
    schemas = {"post": segment_schema}

    @handle_errors
    async def get(self, segment_id: str):
        segment = await self.service.get_segment(int(segment_id))
        contacts = await self.service.list_contacts_in_segment(int(segment_id))
        self.write(
            self.loader.load("segments/segment.html").generate(
                segment=segment, contacts=contacts
            )
        )

    @handle_errors
    async def post(self, segment_id: str):
        data = self.get_data("post")
        data["id"] = int(segment_id)
        await self.service.update_contact(data)
        await self.get(segment_id)


class SegmentFormHandler(BaseSegmentRequestHandler):
    @handle_errors
    async def get(self, segment_id: Optional[str] = None):
        if segment_id:
            action = f"/segments/{segment_id}"
            initial = await self.service.get_segment(int(segment_id))
        else:
            action = "/segments"
            initial = {}

        self.write(
            self.loader.load("segments/segment_form.html").generate(
                action=action, initial=initial
            )
        )
