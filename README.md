# Description
Pretty simple WebSocketServer that reads from a broker and send the response to the client based on session_id.    
The server is using JWE-token for users' data.  
Session_id will be using as a routing key for the auto-deleted queue.

# Config and run
Most of the setting would be got from envs.
```python
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
    "key": os.getenv("JWE_KEY"),
    "algorithms": ["HS256"]
}

origin = {"my.website.com"}
```
## Plain run
1. `pip install -e .` - for the module installation.
2. `JWE_KEY="secret_key" WEBSOCKET_AMQP_CONNECTION="amqp://test_user:testuser@localhost:5672/test_vhost" WEBSOCKET_DEBUG_TOKEN=True WebSocketServer` - for run the server locally
3. You can also use `run.sh` script.

## Docker
The `.env.prod` file should be filled before the containers will be launched.
For example:

```shell script
JWE_KEY=secret_key
RABBITMQ_DEFAULT_VHOST=admin
RABBITMQ_DEFAULT_USER=admin
RABBITMQ_DEFAULT_PASS=secret_password
WEBSOCKET_AMQP_CONNECTION="amqp://admin:secret_password@localhost:5672/admin"
```

## Debug 
```WEBSOCKET_DEBUG_TOKEN=True``` option could be used for debugging purposes.  
##### !!Warning!!
You should not use this option in production.
It disables JWE-authorization middleware and create a mock token inside the UserSession.process() with the following parameters:
```python
{
"expired": now()+timedelta(hours=6),
"session_id": random.choice([321, 123, 333, 45])
} 
``` 


## Tests
`settings_dev.py` will be using for the tests.
Running tests could be look like this:
```shell script
JWE_KEY="secret_key" WEBSOCKET_AMQP_CONNECTION="amqp://test_user:testuser@localhost:5672/test_vhost" pytest
```
