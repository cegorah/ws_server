import os

AMQP_SETTINGS = {
    "cafile": os.getenv("RMQ_CA_PATH") or "./ca-cert.pem",
    "certfile": os.getenv("RMQ_CERT_PATH") or "./cert-signed.pem",
    "keyfile": os.getenv("RMQ_KEY_FILE") or "./cert-key.pem",
    "topic_exchange_name": "recognition.food.tx",
    "exchange_type": "topic",
}
auth_settings = {
    "expires_seconds": 6
}

jwe_settings = {
    "key": os.getenv("JWE_KEY") or "secret_key",
    "algorithms": ["HS256"]
}

origin = {"my.website.com"}
