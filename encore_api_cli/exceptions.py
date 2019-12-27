class ClientError(Exception):
    pass


class InvalidFileType(ClientError):
    pass


class RequestsError(ClientError):
    pass
