import ssl
import weakref
from aiohttp import web
from asyncio import all_tasks, current_task, gather, get_running_loop, CancelledError
from aiomisc.log import basic_config
from configargparse import ArgumentParser, ArgumentDefaultsHelpFormatter, Namespace

from WebSocketServer.errors import *
from WebSocketServer.middlewares import *
from WebSocketServer.settings import AMQP_SETTINGS
from WebSocketServer.broker.rmq_client import RabbitClient

from WebSocketServer.sockets.routes import ws_handler

logger = logging.getLogger(__name__)


def create_parser() -> ArgumentParser:
    parser = ArgumentParser(
        auto_env_var_prefix="WEBSOCKET_",
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--api-address', default='0.0.0.0',
                        help='IPv4/IPv6 address API server would listen on')
    parser.add_argument('--api-port', default=8081,
                        help='TCP port API server would listen on')
    parser.add_argument('--log-level', default="ERROR",
                        help='default logging level')
    parser.add_argument('--amqp-connection', default="amqp://admin:admin@localhost:5672/test_vhost",
                        help='a connection string that will be used for connect to the broker')
    parser.add_argument('--debug_token', default=False, type=bool,
                        help='WARNING! Should not be used in production. '
                             'jwt_authorization middleware will be disabled. '
                             'Create a debug token inside the UserSession.process() with the following parameters: '
                             '{"expired": now()+timedelta(hours=6);"session_id": random.choice([321, 123, 333, 45]}')
    return parser


def get_args() -> Namespace:
    parser = create_parser()
    args, _ = parser.parse_known_args()
    return args


def ssl_options():
    return dict(
        ca_certs=AMQP_SETTINGS.get("cafile"),
        certfile=AMQP_SETTINGS.get("certfile"),
        keyfile=AMQP_SETTINGS.get("keyfile"),
        cert_reqs=ssl.CERT_REQUIRED
    )


async def init_app(arguments: Namespace = None) -> web.Application:
    args = arguments or get_args()
    middlewares = [jwt_authorization] if not args.debug_token else list()
    app = web.Application(middlewares=middlewares)
    app["args"] = args
    app["broker"] = RabbitClient(connection_string=args.amqp_connection, robust=False, pool=False,
                                 ssl_options=ssl_options(),
                                 exchange_name=AMQP_SETTINGS.get("topic_exchange_name"),
                                 exchange_type=AMQP_SETTINGS.get("exchange_type"))
    app["sessions"] = weakref.WeakSet()
    basic_config(level=log_level(args.log_level))
    app.add_routes([
        web.get("/ws", ws_handler)
    ])
    app.on_startup.append(init_services)
    app.on_cleanup.append(cleanup)
    return app


def log_level(level):
    levels = {"debug": logging.DEBUG, "info": logging.INFO, "error": logging.ERROR, "warning": logging.WARNING}
    return levels.get(level.lower())


async def init_services(app):
    broker = app.get("broker")
    assert broker, "The broker object should be provided by app dictionary"
    await broker.init_broker()
    loop = get_running_loop()
    loop.set_exception_handler(general_error_handler)


def general_error_handler(loop, context):
    exception = context.get("exception")
    if isinstance(exception, BrokerSendError):
        logger.error(f"Could not send the message to the broker with the error {exception}")
        return
    if isinstance(exception, TokenError):
        logger.error(f"Can't read the token with message {exception}")


async def cleanup(app):
    try:
        sessions = app.get("sessions")
        for ses in sessions:
            await ses.close()
        sessions.clear()
        await app.get("broker").close()
        tasks = [t for t in all_tasks() if t is not current_task()]
        [task.cancel() for task in tasks]
        await gather(*tasks, return_exceptions=True)
    except CancelledError:
        pass
