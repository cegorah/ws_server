import datetime
import asyncio
import logging
import random
from weakref import WeakSet

from aiohttp.web import Request, WebSocketResponse

from WebSocketServer.errors import *
from WebSocketServer.setupable import Setupable

logger = logging.getLogger(__name__)


class UserSession(Setupable):
    def __init__(self, request: Request):
        super().__init__(request)
        self.loop = asyncio.get_running_loop()
        self.__ws_channel = WebSocketResponse(heartbeat=2)
        self.debug_token = request.app.get("args").debug_token
        self.tasks = WeakSet()

    async def process(self, request):
        channel = self.__ws_channel
        loop = self.loop
        tasks = self.tasks
        await channel.prepare(request)
        token_dict = request.get("token_dict")
        debug_dict = {
            "expires": datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(hours=6),
                                                  "%a, %d %b %Y %H:%M:%S GMT"),
            "session_id": random.choice(["aab", "aac", "ddd"])
        }
        if self.debug_token:
            token_dict = debug_dict
        try:
            expires = datetime.datetime.strptime(token_dict.get("expires"), "%a, %d %b %Y %H:%M:%S GMT")
            sess_id = str(token_dict.get("session_id"))
            timeout = loop.create_task(
                self.timeout(expires)
            )
            tasks.add(timeout)
        except (ValueError, AttributeError) as e:
            await channel.close()
            logger.error(e)
            raise TokenError(e)
        try:
            channel_name = f"recognition_{sess_id}_tq"
            routing_key = f"food.image.{sess_id}"
            tasks.add(loop.create_task(
                self.broker.listen(channel_name=channel_name, durable=False, auto_delete=True,
                                   routing_key=routing_key, exclusive=True)
            )
            )
            tasks.add(loop.create_task(
                self.send_result(routing_key)
            ))
            async for mes in channel:
                if timeout.done():
                    break
        except Exception as e:
            logger.error(e)
        finally:
            await self.close()

    async def timeout(self, expires):
        try:
            while datetime.datetime.now() < expires:
                await asyncio.sleep(1)
            await self.close()
        except Exception as e:
            logger.error(e)

    async def send_result(self, sess_id):
        try:
            while True:
                mess = await self.broker.get_result(sess_id)
                if mess:
                    await self.__ws_channel.send_str(mess)
                await asyncio.sleep(1)
        except Exception as e:
            raise SessionError(e.__str__())

    async def close(self, code=1000, message=None):
        [task.cancel() for task in self.tasks]
        if not self.__ws_channel.closed:
            await self.__ws_channel.close(code=code, message=message)
        await self.broker.channel_cleanup()

    @property
    def response(self):
        assert self.__ws_channel.prepared, \
            f"Use {self.__class__.__name__}.process() first to prepare the response"
        return self.__ws_channel
