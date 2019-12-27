class ClientException(Exception):
    pass


class InvalidFileType(ClientException):
    pass


class RequestsError(ClientException):
    pass


class SettingsException(Exception):
    pass


class SettingsValueError(SettingsException):
    pass
