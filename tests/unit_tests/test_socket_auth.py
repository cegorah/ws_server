from aiohttp.web_ws import WSMsgType, WSMessage, WebSocketResponse


async def test_invalid_origins(api_ws_cli):
    resp = await api_ws_cli.ws_connect('/ws',
                                       headers={
                                           'Upgrade': 'websocket',
                                           'Sec-WebSocket-Extensions': 'permessage-deflate',
                                           'Sec-WebSocket-Key': 'yE4TmCX7xmZ815muKPbHbA==',
                                           'Connection': 'keep-alive, Upgrade',
                                       },
                                       heartbeat=2)
    res = await resp.receive()
    assert res[2] == "Unauthorized"


async def test_no_token(api_ws_cli):
    resp = await api_ws_cli.ws_connect('/ws',
                                       headers={
                                           'Upgrade': 'websocket',
                                           'Sec-WebSocket-Extensions': 'permessage-deflate',
                                           'Sec-WebSocket-Key': 'yE4TmCX7xmZ815muKPbHbA==',
                                           'Connection': 'keep-alive, Upgrade',
                                           'Origin': 'my.website.com'
                                       },
                                       heartbeat=2)
    res = await resp.receive()
    assert res[2] == "Unauthorized"


async def test_no_token_expires(api_ws_cli, create_token):
    resp = await api_ws_cli.ws_connect('/ws',
                                       headers={
                                           'Upgrade': 'websocket',
                                           'Sec-WebSocket-Extensions': 'permessage-deflate',
                                           'Sec-WebSocket-Key': 'yE4TmCX7xmZ815muKPbHbA==',
                                           'Connection': 'keep-alive, Upgrade',
                                           'Token': create_token(expired=False),
                                           'Origin': 'my.website.com'
                                       },
                                       heartbeat=2)
    res = await resp.receive()
    assert res[2] == "Unauthorized"


async def test_no_token_session(api_ws_cli, create_token):
    resp = await api_ws_cli.ws_connect('/ws',
                                       headers={
                                           'Upgrade': 'websocket',
                                           'Sec-WebSocket-Extensions': 'permessage-deflate',
                                           'Sec-WebSocket-Key': 'yE4TmCX7xmZ815muKPbHbA==',
                                           'Connection': 'keep-alive, Upgrade',
                                           'Token': create_token(session_id=None),
                                           'Origin': 'my.website.com'
                                       },
                                       heartbeat=2)
    res = await resp.receive()
    assert res[2] == "Unauthorized"


async def test_no_origin(api_ws_cli, create_token):
    resp = await api_ws_cli.ws_connect('/ws',
                                       headers={
                                           'upgrade': 'websocket',
                                           'Sec-WebSocket-Extensions': 'permessage-deflate',
                                           'Sec-WebSocket-Key': 'yE4TmCX7xmZ815muKPbHbA==',
                                           'Connection': 'keep-alive, Upgrade',
                                           'token': create_token(),
                                       },
                                       heartbeat=2)
    res = await resp.receive()
    await resp.close()
    assert res[1] == 4001


async def test_proper_auth(api_ws_cli, create_token):
    token = create_token()
    resp: WebSocketResponse = await api_ws_cli.ws_connect('/ws',
                                       headers={
                                           'upgrade': 'websocket',
                                           'Sec-WebSocket-Extensions': 'permessage-deflate',
                                           'Sec-WebSocket-Key': 'yE4TmCX7xmZ815muKPbHbA==',
                                           'Connection': 'keep-alive, Upgrade',
                                           'token': token,
                                           'Origin': 'my.website.com'
                                       },
                                       heartbeat=2)
    res: WSMessage = await resp.receive()
    await resp.close()
    assert res.type == WSMsgType.CLOSED
