import logging
from aiohttp.web import Request
from WebSocketServer.sockets.user_session import UserSession as SocketSession

logger = logging.getLogger(__name__)


# TODO Add wss for ssl/tls
async def ws_handler(request: Request):
    ses = SocketSession(request)
    request.app["sessions"].add(ses)
    await ses.process(request)
    return ses.response
