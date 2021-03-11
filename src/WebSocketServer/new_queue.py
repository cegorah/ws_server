import asyncio
import aio_pika
from WebSocketServer.settings import AMQP_SETTINGS


async def main():
    cn: aio_pika.Connection = await aio_pika.connect("amqp://admin:admin@localhost:5672/test_vhost")
    ch: aio_pika.RobustChannel = await cn.channel()
    exch: aio_pika.Exchange = await ch.declare_exchange(name=AMQP_SETTINGS.get("topic_exchange_name"), type="topic")
    queue = await ch.declare_queue("tq", auto_delete=True)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
