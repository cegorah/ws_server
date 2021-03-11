from WebSocketServer.broker.IBroker import BrokerInterface


class Setupable(object):
    def __init__(self, request):
        self.request = request
        self.broker: BrokerInterface = request.app.get("broker")
