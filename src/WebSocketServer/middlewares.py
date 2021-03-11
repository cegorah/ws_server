from aiohttp.web import middleware, HTTPForbidden, Request, WebSocketResponse
from jwt import decode as jwt_decode, DecodeError, InvalidTokenError
from WebSocketServer.settings import jwe_settings, origin
import logging

log = logging.getLogger(__name__)


@middleware
async def jwt_authorization(request: Request, handler):
    origins = await _check_origins(request)
    socket = True if request.headers.get("Upgrade") == "websocket" else False
    token = request.headers.get("token")
    try:
        jwt_decode(token, **jwe_settings)
        request["token_dict"] = await _jwt_access_token_decode(token)
        if not all(request["token_dict"].values()) or not origins:
            return await _socket_unauth(request) if socket else HTTPForbidden()
    except Exception as e:
        log.error(f"Can't decode the token:\n{e}")
        return await _socket_unauth(request) if socket else HTTPForbidden()
    resp = await handler(request)
    return resp


async def _check_origins(request):
    if request.headers.get("Origin") not in origin:
        return False
    return True


async def _jwt_access_token_decode(token):
    try:
        decoded = jwt_decode(token.encode(), **jwe_settings)
        return {"expires": decoded.get("expires"), "session_id": decoded.get("session_id")}
    except DecodeError as e:
        log.error(e)
        raise InvalidTokenError("Invalid token")


async def _socket_unauth(request):
    resp = WebSocketResponse()
    await resp.prepare(request)
    await resp.close(code=4001, message="Unauthorized".encode())
    return resp
