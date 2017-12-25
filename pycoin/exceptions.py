class PyCoinException(Exception):
    message = ''

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return self.message


class NotEnoughBalanceError(PyCoinException):
    message = "Not enough balance"
