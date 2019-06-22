from typing import Dict

from aiohttp import ClientSession
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


def initialize_redis_pool(redis_config: Dict):
    pass


def initialize_web_session(web_session_config: Dict) -> ClientSession:
    pass


def initialize_email_gateway_session(email_session_config: Dict) -> ClientSession:
    pass


async def initialize_services(config: Dict):
    redis = await initialize_redis_pool(config["redis"])
    web_session = initialize_web_session(config["sessions"]["web"])
    email_session = initialize_email_gateway_session(config["sessions"]["email"])

    web_client = WebClient(config["web"]["url"], web_session,
                           config["web"]["retry_count"], config["web"]["retry_backoff"])
    email_client = FlypsGatewayClient(
        config["email"]["url"], email_session,
    )

    settings_storage = SimpleRedisSettingsStorage(redis)

    email_service = SendEmailService(web_client, email_client, settings_storage,
                                     config["service"]["email"]["batch_size"],
                                     config["service"]["email"]["retry_count"],
                                     config["service"]["email"]["retry_backoff"])
    settings_service = SettingsService(settings_storage)

    return email_service, settings_service


def make_app(
        settings_service: AbstractSettingsService,
        email_service: AbstractSendEmailService
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
