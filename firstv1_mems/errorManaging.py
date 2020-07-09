################################################################################
##################          Error class definition          ####################
################################################################################


class MyException(BaseException):
    # Class made to catch errors coming from the subscriber com
    # See in class ComPortSUB
    def __init__(self, current_exception):
        self.current_exception = current_exception

    def __str__(self):
        return str(self.current_exception)