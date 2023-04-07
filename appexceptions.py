from http import HTTPStatus

class AppException(Exception):
    def __init__(self, message: str, status: HTTPStatus) -> None:
        self.message = message
        self.status = status
        super().__init__(self.message)


class ConflictingPicksetException(AppException):
    def __init__(self, message: str, status: HTTPStatus) -> None:
        self.message = message
        self.status = status
        super().__init__(self.message, status)
