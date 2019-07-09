from asynctest import create_autospec
from tornado.template import Loader
from tornado.testing import AsyncHTTPTestCase

from web.app import make_app
from web.services.contact.abstract import AbstractContactService
from web.services.email.abstract import AbstractEmailService
from web.services.settings.abstract import AbstractSettingsService


class BaseHandlerTest(AsyncHTTPTestCase):
    def setUp(self):
        self.template_loader = create_autospec(Loader)
        self.template_loader.load.return_value.generate.return_value = "I am template"
        self.contact_service = create_autospec(AbstractContactService)
        self.email_service = create_autospec(AbstractEmailService)
        self.settings_service = create_autospec(AbstractSettingsService)
        super().setUp()

    def get_app(self):
        return make_app(
            self.template_loader,
            self.contact_service,
            self.email_service,
            self.settings_service,
        )
