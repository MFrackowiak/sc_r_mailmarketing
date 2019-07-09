import os
from asyncio import get_event_loop
from json import load
from typing import Dict

from aiohttp import ClientSession, ClientTimeout
from aioredis import create_redis_pool
from tornado.web import Application

from email_client.controllers.email import EmailHandler
from email_client.controllers.settings import SettingsHandler
from email_client.integrations.email.flyps import FlypsGatewayClient
from email_client.integrations.web.client import WebClient
from email_client.services.email.abstract import AbstractSendEmailService
from email_client.services.email.service import SendEmailService
from email_client.services.settings.abstract import AbstractSettingsService
from email_client.services.settings.service import SettingsService
from email_client.settings.redis import SimpleRedisSettingsStorage


async def initialize_redis_pool(redis_config: Dict):
    redis_pool = await create_redis_pool(
        redis_config["host"],
        minsize=redis_config.get("min_size", 5),
        maxsize=redis_config.get("min_size", 10),
        loop=get_event_loop(),
        timeout=5,
    )
    return redis_pool


def initialize_web_session(web_session_config: Dict) -> ClientSession:
    return ClientSession(timeout=ClientTimeout(**web_session_config["timeout"]))


def initialize_email_gateway_session(email_session_config: Dict) -> ClientSession:
    return ClientSession(timeout=ClientTimeout(**email_session_config["timeout"]))


async def initialize_services(config: Dict):
    redis = await initialize_redis_pool(config["redis"])
    web_session = initialize_web_session(config["sessions"]["web"])
    email_session = initialize_email_gateway_session(config["sessions"]["email"])

    web_client = WebClient(
        config["web"]["url"],
        web_session,
        config["web"]["retry_count"],
        config["web"]["retry_backoff"],
    )
    email_client = FlypsGatewayClient(config["email"]["url"], email_session)

    settings_storage = SimpleRedisSettingsStorage(redis)

    email_service = SendEmailService(
        web_client,
        email_client,
        settings_storage,
        config["email"]["batch_size"],
        config["email"]["retry_count"],
        config["email"]["retry_backoff"],
    )
    settings_service = SettingsService(settings_storage)

    return email_service, settings_service


def make_app(
    settings_service: AbstractSettingsService, email_service: AbstractSendEmailService
):
    return Application(
        [
            (
                r"/api/v1/settings",
                SettingsHandler,
                {"settings_service": settings_service},
            ),
            (r"/api/v1/email", EmailHandler, {"email_service": email_service}),
        ]
    )


async def init_app():
    app_config_file = os.environ.get("SCMM_EMAIL_CONFIG", "app-email.json")

    with open(app_config_file) as config_file:
        app_config = load(config_file)

    email_service, settings_service = await initialize_services(app_config)

    app = make_app(settings_service, email_service)

    return app, app_config
