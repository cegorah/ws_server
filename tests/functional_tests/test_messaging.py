import random
import asyncio
import aio_pika
from functools import partial
from asyncio import Queue
from WebSocketServer.broker.rmq_client import RabbitClient
from WebSocketServer.settings_dev import origin


async def test_client_init(loop, rabbit_client, publisher):
    rk = "route_me"
    rc: RabbitClient = await rabbit_client("hello_queue", auto_delete=True, exclusive=True, routing_key=rk)
    pb: aio_pika.Exchange = await publisher()

    async def _get_res(rk):
        res = None
        while not res:
            res = await rc.get_result(rk)
            await asyncio.sleep(1)
        return res

    def put_mess(res: Queue, fut: asyncio.Future):
        res.put_nowait(fut.result())

    t = loop.create_task(_get_res(rk))
    res = Queue()
    t.add_done_callback(partial(put_mess, res))
    body = "message"
    ms = aio_pika.Message(body.encode())
    await pb.publish(ms, routing_key=rk)
    assert await res.get() == body


async def test_client_receive(api_ws_cli, create_token, publisher):
    sess_id = random.choice(range(1, 6))
    routing_key = f"food.image.{sess_id}"
    resp = await api_ws_cli.ws_connect('/ws',
                                       headers={
                                           'upgrade': 'websocket',
                                           'Sec-WebSocket-Extensions': 'permessage-deflate',
                                           'Sec-WebSocket-Key': 'yE4TmCX7xmZ815muKPbHbA==',
                                           'Connection': 'keep-alive, Upgrade',
                                           'token': create_token(session_id=sess_id),
                                           'origin': origin.pop()
                                       },
                                       heartbeat=2)
    pb: aio_pika.Exchange = await publisher()
    body = "message"
    ms = aio_pika.Message(body.encode())
    await pb.publish(ms, routing_key=routing_key)
    res = await resp.receive()
    assert res.data == body
    await resp.close()
