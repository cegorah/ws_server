class BrokerException(BaseException):
    pass


class BrokerSendError(BrokerException):
    def __init__(self, message: str = None):
        self.message = message
        super().__init__(self.message)


class BrokerReadError(BrokerException):
    def __init__(self, message: str = None):
        self.message = message
        super().__init__(self.message)
