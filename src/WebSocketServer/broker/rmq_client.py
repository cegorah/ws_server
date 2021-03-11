import logging
import aio_pika
from typing import Dict, Any, Union
from asyncio import get_running_loop
from WebSocketServer.broker.IBroker import BrokerInterface
from WebSocketServer.errors.broker_errors import *

logger = logging.getLogger(__name__)


class RabbitClient(BrokerInterface):
    def __init__(self, *, connection_string: str, robust: bool, **kwargs):
        self.robust = robust
        self.queues = dict()
        self.connection_string = connection_string
        self.dispatch_args(kwargs)

        self.raw_connection = None
        self.connection_pool = None
        self.channel_pool = None
        self.channel = None
        self.exchange = None

    def dispatch_args(self, arguments: Dict[str, Any]):
        self.ssl_options = arguments.get("ssl_options")
        self.pool = arguments.get("connection_pool", True)
        self.c_pool_size = arguments.get("connection_pool_size", 2)
        self.ch_pool_size = arguments.get("channel_pool_size", 10)
        self.exchange_name = arguments.get("exchange_name", "recognition.food.dx")
        self.exchange_type = arguments.get("exchange_type", "direct")

    async def init_broker(self):
        loop = get_running_loop()
        if self.pool:
            self.connection_pool = aio_pika.pool.Pool(self._get_connection, max_size=self.c_pool_size, loop=loop)
            self.channel_pool = aio_pika.pool.Pool(self._get_channel, max_size=self.ch_pool_size, loop=loop)
            self.channel = await self._get_channel()
            self.exchange: aio_pika.Exchange = await self.channel.declare_exchange(name=self.exchange_name,
                                                                                   type=self.exchange_type)
        else:
            self.raw_connection = await self._get_connection()
            self.channel = await self.raw_connection.channel()
            self.exchange: aio_pika.Exchange = await self.channel.declare_exchange(self.exchange_name,
                                                                                   type=self.exchange_type)

    async def _get_connection(self) -> Union[aio_pika.RobustConnection, aio_pika.Connection]:
        if self.robust:
            return await aio_pika.connect_robust(self.connection_string, ssl=True,
                                                 ssl_options=self.ssl_options)
        return await aio_pika.connect(self.connection_string, ssl=True,
                                      ssl_options=self.ssl_options)

    async def _get_channel(self) -> Union[aio_pika.Channel, aio_pika.RobustChannel]:
        async with self.connection_pool.acquire() as connection:
            return await connection.channel()

    async def listen(self, *, channel_name: str, **kwargs):
        assert any(
            [self.raw_connection, self.connection_pool]), "Use init_broker() first to initialize a connection"
        try:
            routing_key = kwargs.pop("routing_key")
        except KeyError:
            routing_key = channel_name
        try:
            channel = self.channel
            queue: aio_pika.Queue = await channel.declare_queue(channel_name, **kwargs)
            await queue.bind(exchange=self.exchange, routing_key=routing_key)
            self.queues[routing_key] = queue
        except Exception as e:
            logger.error(e)
            raise e

    async def channel_cleanup(self):
        logger.debug("cleanup the exchange")
        for routing_key, queue in self.queues.items():
            try:
                await queue.unbind(self.exchange, routing_key=routing_key)
                await queue.delete()
            except Exception as e:
                logger.error(e)
        await self.channel.close()

    async def get_result(self, key):
        try:
            queue: aio_pika.Queue = self.queues.get(key)
            if queue:
                message: aio_pika.IncomingMessage = await queue.get(fail=False, no_ack=True)
                if message:
                    return message.body.decode()
            return None
        except Exception as e:
            raise BrokerSendError(e.__str__())

    async def send(self, *, channel_name: str, **kwargs):
        raise NotImplementedError("Simple listener")

    async def close(self):
        try:
            if self.connection_pool:
                await self.channel_pool.close()
                await self.connection_pool.close()
            else:
                await self.channel.close()
                await self.raw_connection.close()
        except Exception as e:
            raise e
