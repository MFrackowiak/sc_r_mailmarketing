from asyncio import get_event_loop

from tornado.platform.asyncio import AsyncIOMainLoop

from email_client.app import init_app

if __name__ == "__main__":
    AsyncIOMainLoop().install()
    loop = get_event_loop()

    app, config = loop.run_until_complete(init_app())
    app.listen(config["port"])
    loop.run_forever()
