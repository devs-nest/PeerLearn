class NetworkError(Exception):
    def __init___(self, dErrorArguments):
        Exception.__init__(self, "{0}".format(dErrorArguments))
        # Exception.__init__(self, "Network Error")


class BadRequest(Exception):
    def __init__(self, message, request):
        self.message = message
        self.request = request

    def __str__(self):
        return repr(self.message)


class UserNotConnected(Exception):
    def __init___(self, dErrorArguments):
        Exception.__init__(self, "{0}".format(dErrorArguments))
        # Exception.__init__(self, "User Not Connected")
