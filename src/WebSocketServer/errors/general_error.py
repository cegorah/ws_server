class GeneralException(BaseException):
    pass


class TokenError(GeneralException):
    def __init__(self, message=None):
        self.message = message
        super().__init__(self.message)


class SessionError(GeneralException):
    def __init__(self, message=None):
        self.message = message
        super().__init__(self.message)
