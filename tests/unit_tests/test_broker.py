async def test_rabbit_listen(rabbit_client):
    routing_key = "routing_key"
    channel_name = "typical"
    client = await rabbit_client(channel_name, auto_delete=True, exclusive=True, routing_key=routing_key)
    assert routing_key in client.queues.keys()
    await client.close()
