import os
from sys import argv
from aiohttp.web import run_app
from setproctitle import setproctitle

from WebSocketServer.connection_routine import init_app, get_args


def main():
    setproctitle(os.path.basename(argv[0]))

    args = get_args()
    run_app(init_app(args), host=args.api_address, port=args.api_port)


if __name__ == "__main__":
    main()
