from tornado.template import Loader

from common.enums import EmailResult
from web.controllers.utils.errors import handle_errors
from web.controllers.utils.validated import ValidatedFormRequestHandler
from web.schemas import campaign_schema
from web.services.contact.abstract import AbstractContactService
from web.services.email.abstract import AbstractEmailService

DEFAULT_PER_PAGE = 25
LABEL_MAPPING = {
    EmailResult.PENDING.value: "blue",
    EmailResult.RECOVERABLE_FAILURE.value: "yellow",
    EmailResult.AUTH_FAILURE.value: "orange",
    EmailResult.FAILURE.value: "red",
    EmailResult.SUCCESS.value: "green",
}


class BaseCampaignRequestHandler(ValidatedFormRequestHandler):
    def initialize(
        self,
        template_loader: Loader,
        email_service: AbstractEmailService,
        contact_service: AbstractContactService,
    ):
        self.email_service = email_service
        self.loader = template_loader
        self.contact_service = contact_service


class CampaignsHandler(BaseCampaignRequestHandler):
    schemas = {"post": campaign_schema}

    @handle_errors
    async def get(self):
        contacts = await self.email_service.get_email_requests()
        self.write(
            self.loader.load("campaigns/campaigns.html").generate(
                objects=contacts, columns=["id", "name"], url_base="/campaigns/"
            )
        )

    @handle_errors
    async def post(self):
        data = self.get_data("post")
        campaign, error = await self.email_service.send_emails(**data)
        self.redirect(f"/campaigns/{campaign['id']}")


class CampaignHandler(BaseCampaignRequestHandler):
    @handle_errors
    async def get(self, campaign_id: str):
        campaign = await self.email_service.get_email_request_details(int(campaign_id))
        self.write(
            self.loader.load("campaigns/campaign.html").generate(
                campaign=campaign["request"],
                jobs=campaign["jobs"],
                labels=LABEL_MAPPING,
            )
        )


class CampaignFormHandler(BaseCampaignRequestHandler):
    @handle_errors
    async def get(self):
        action = "/campaigns"
        templates = await self.email_service.list_email_templates()
        segments = await self.contact_service.read_segments(1, None)

        self.write(
            self.loader.load("campaigns/campaign_form.html").generate(
                action=action, segments=segments, templates=templates
            )
        )
