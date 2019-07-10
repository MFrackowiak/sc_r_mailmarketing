from asyncio import get_event_loop

from tornado.platform.asyncio import AsyncIOMainLoop

from mock.app import init_app

if __name__ == "__main__":
    AsyncIOMainLoop().install()
    loop = get_event_loop()

    app = init_app()
    app.listen(5004)
    loop.run_forever()
