import os
from json import load

from aiohttp import ClientSession
from aiopg.sa import create_engine
from tornado.template import Loader
from tornado.web import Application

from web.controllers.campaign import (
    CampaignFormHandler,
    CampaignsHandler,
    CampaignHandler,
)
from web.controllers.contact import (
    ContactsHandler,
    ContactHandler,
    ContactFormHandler,
    ContactSegmentFormHandler,
)
from web.controllers.dashboard import Dashboard
from web.controllers.job import JobStatusHandler
from web.controllers.segment import SegmentsHandler, SegmentHandler, SegmentFormHandler
from web.controllers.settings import SettingsRequestHandler
from web.controllers.template import (
    TemplatesHandler,
    TemplateFormHandler,
    TemplateHandler,
)
from web.integrations.email_client.http import EmailHTTPClient
from web.repositories.contact.aiopg import SimplePostgresContactRepository
from web.repositories.jobs.aiopg import SimplePostgresJobRepository
from web.services.contact.abstract import AbstractContactService
from web.services.contact.service import ContactService
from web.services.email.abstract import AbstractEmailService
from web.services.email.service import EmailService
from web.services.settings.abstract import AbstractSettingsService
from web.services.settings.service import SettingsService


async def init_db(config_file: str, force_init_db=False):
    with open(config_file) as dbconfig:
        config = load(dbconfig)

    engine = await create_engine(
        user=config["user"],
        database=config["name"],
        host=config["host"],
        password=config["password"],
    )

    if force_init_db:
        with open(config["sql"]) as sql_file:
            init_sql = sql_file.read()

        async with engine.acquire() as conn:
            await conn.execute(init_sql)

    return engine


def create_contact_app(
    template_loader: Loader, contact_service: AbstractContactService
) -> Application:
    shared_kwargs = {
        "template_loader": template_loader,
        "contact_service": contact_service,
    }
    return Application(
        [
            (r"/contacts", ContactsHandler, shared_kwargs),
            (r"/contacts/(?P<contact_id>\d+)", ContactHandler, shared_kwargs),
            (r"/contacts/add", ContactFormHandler, shared_kwargs),
            (r"/contacts/(?P<contact_id>\d+)/edit", ContactFormHandler, shared_kwargs),
            (
                r"/contacts/(?P<contact_id>\d+)/segments",
                ContactSegmentFormHandler,
                shared_kwargs,
            ),
        ]
    )


def create_segment_app(
    template_loader: Loader, contact_service: AbstractContactService
) -> Application:
    shared_kwargs = {
        "template_loader": template_loader,
        "contact_service": contact_service,
    }
    return Application(
        [
            (r"/segments", SegmentsHandler, shared_kwargs),
            (r"/segments/(?P<segment_id>\d+)", SegmentHandler, shared_kwargs),
            (r"/segments/add", SegmentFormHandler, shared_kwargs),
            (r"/segments/(?P<segment_id>\d+)/edit", SegmentFormHandler, shared_kwargs),
        ]
    )


def create_templates_app(
    template_loader: Loader, email_service: AbstractEmailService
) -> Application:
    shared_kwargs = {"template_loader": template_loader, "email_service": email_service}
    return Application(
        [
            (r"/templates", TemplatesHandler, shared_kwargs),
            (r"/templates/(?P<template_id>\d+)", TemplateHandler, shared_kwargs),
            (r"/templates/add", TemplateFormHandler, shared_kwargs),
            (
                r"/templates/(?P<template_id>\d+)/edit",
                TemplateFormHandler,
                shared_kwargs,
            ),
        ]
    )


def create_campaign_app(
    template_loader: Loader,
    email_service: AbstractEmailService,
    contact_service: AbstractContactService,
) -> Application:
    shared_kwargs = {
        "template_loader": template_loader,
        "email_service": email_service,
        "contact_service": contact_service,
    }
    return Application(
        [
            (r"/campaigns", CampaignsHandler, shared_kwargs),
            (r"/campaigns/(?P<campaign_id>\d+)", CampaignHandler, shared_kwargs),
            (r"/campaigns/create", CampaignFormHandler, shared_kwargs),
        ]
    )


def make_app(
    template_loader: Loader,
    contact_service: AbstractContactService,
    email_service: AbstractEmailService,
    settings_service: AbstractSettingsService,
):
    return Application(
        [
            (r"/", Dashboard, {"template_loader": template_loader}),
            (r"/contacts.*", create_contact_app(template_loader, contact_service)),
            (r"/segments.*", create_segment_app(template_loader, contact_service)),
            (r"/templates.*", create_templates_app(template_loader, email_service)),
            (
                r"/settings",
                SettingsRequestHandler,
                {
                    "template_loader": template_loader,
                    "settings_service": settings_service,
                },
            ),
            (
                r"/campaigns.*",
                create_campaign_app(template_loader, email_service, contact_service),
            ),
            (r"/job", JobStatusHandler, {"email_service": email_service}),
        ]
    )


async def init_app():
    app_config_file = os.environ.get("SCMM_APP_CONFIG", "application.json")
    db_config_file = os.environ.get("SCMM_DB_CONFIG", "database.json")

    db_engine = await init_db(db_config_file)

    with open(app_config_file) as config_file:
        app_config = load(config_file)

    contact_repository = SimplePostgresContactRepository(db_engine)
    job_repository = SimplePostgresJobRepository(db_engine)

    email_client = EmailHTTPClient(ClientSession(), app_config["email"]["url"])

    contact_service = ContactService(contact_repository)
    email_service = EmailService(job_repository, email_client)
    settings_service = SettingsService(email_client)

    template_loader = Loader("templates")

    app = make_app(template_loader, contact_service, email_service, settings_service)

    return app, app_config
