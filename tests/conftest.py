import os
import pytest
import logging
import aio_pika
import asyncio
from random import randint
from jwt import encode as jwt_encode
from datetime import datetime, timedelta
from WebSocketServer.connection_routine import init_app
from WebSocketServer.broker.rmq_client import RabbitClient
from WebSocketServer.settings_dev import jwe_settings, AMQP_SETTINGS

log = logging.getLogger(__name__)

exchange_name = AMQP_SETTINGS.get("topic_exchange_name")
exchange_type = AMQP_SETTINGS.get("exchange_type")


@pytest.fixture
def api_ws_cli(loop, aiohttp_client):
    app = loop.run_until_complete(init_app())
    yield loop.run_until_complete(aiohttp_client(app))


@pytest.fixture
def publisher(loop) -> aio_pika.Exchange:
    async def _publisher():
        url = os.getenv("WEBSOCKET_AMQP_CONNECTION")
        connection: aio_pika.RobustConnection = await aio_pika.connect(
            url=url)
        channel: aio_pika.Channel = await connection.channel()

        return await channel.declare_exchange(exchange_name,
                                              type=exchange_type)

    yield _publisher


@pytest.fixture
def rabbit_client(loop) -> RabbitClient:
    url = os.getenv("WEBSOCKET_AMQP_CONNECTION")
    client: RabbitClient = RabbitClient(
        connection_string=url,
        robust=True,
        exchange_name=exchange_name,
        exchange_type=exchange_type
    )

    async def _client(channel_name, **kwargs):
        await client.init_broker()
        t = loop.create_task(client.listen(channel_name=channel_name, **kwargs))
        await asyncio.gather(t, return_exceptions=True)
        return client

    yield _client
    loop.run_until_complete(client.channel_cleanup())
    loop.run_until_complete(client.close())


@pytest.fixture
def create_token():
    def _create_token(expired=True, session_id=randint(1, 6), expired_time=None):
        expires = expired_time or datetime.now() + timedelta(seconds=6)
        encode_tk = jwt_encode({
            "session_id": session_id,
            "expires": expires.strftime("%a, %d %b %Y %H:%M:%S GMT") if expired else None,
        }, key=jwe_settings.get("key"))
        return encode_tk

    return _create_token
