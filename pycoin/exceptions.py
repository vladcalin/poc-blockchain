class PyCoinException(Exception):
    message = ''

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return self.message


class ValidationError(PyCoinException):
    message = 'Validation failed: {validation_err}'


class NotEnoughBalanceError(PyCoinException):
    message = "Not enough balance"


class InvalidAddressError(ValidationError):
    def __init__(self, validation_msg):
        self.msg = validation_msg

    def __str__(self):
        return self.message.format(validation_err=self.msg)


class ClientError(PyCoinException):
    pass
