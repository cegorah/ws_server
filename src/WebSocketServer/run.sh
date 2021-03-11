#!/bin/sh
gunicorn connection_routine:init_app --bind 0.0.0.0:8080 --worker-class aiohttp.GunicornWebWorker --reload --workers 16