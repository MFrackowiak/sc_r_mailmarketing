from tornado.template import Loader
from tornado.web import RequestHandler


class Dashboard(RequestHandler):
    def initialize(self, template_loader: Loader):
        self.loader = template_loader

    async def get(self):
        self.write(self.loader.load("dashboard.html").generate())
