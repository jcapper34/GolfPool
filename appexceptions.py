from http import HTTPStatus

class AppException(Exception):
    def __init__(self, message: str, status: HTTPStatus) -> None:
        self.message = message
        self.status = status
        super().__init__(self.message)


class ConflictingPicksetException(AppException):
    def __init__(self, message: str, status: HTTPStatus = HTTPStatus.CONFLICT) -> None:
        self.message = message
        self.status = status
        super().__init__(self.message, status)


class PlayerNotFoundException(AppException):
    def __init__(self, message: str = "Player could not be found", status: HTTPStatus = HTTPStatus.NOT_FOUND) -> None:
        self.message = message
        self.status = status
        super().__init__(self.message, status)


class PicksetNotFoundException(AppException):
    def __init__(self, message: str = "Pickset could not be found", status: HTTPStatus = HTTPStatus.NOT_FOUND) -> None:
        self.message = message
        self.status = status
        super().__init__(self.message, status)


class ApiRequestException(AppException):
    def __init__(self, message: str, status: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR) -> None:
        self.message = message
        self.status = status
        super().__init__(self.message, status)
