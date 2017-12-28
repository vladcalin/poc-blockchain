class PyCoinException(Exception):
    message = ''

    def __init__(self, msg=''):
        self.message = msg

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return self.message


class ValidationError(PyCoinException):
    message = 'Validation failed'


class NotEnoughBalanceError(PyCoinException):
    message = "Not enough balance"


class ClientError(PyCoinException):
    pass
