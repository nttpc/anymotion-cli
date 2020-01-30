class ClientException(Exception):
    pass


class InvalidFileType(ClientException):
    pass


class RequestsError(ClientException):
    pass


class InvalidResponse(ClientException):
    pass
