from http import HTTPStatus


class APIError(Exception):
    """Базовое исключение для API‑ошибок."""

    def __init__(self, message, status_code=HTTPStatus.BAD_REQUEST):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    def to_dict(self):
        """Возвращает словарь для JSON-ответа."""
        return {'message': self.message}


class ValidationError(APIError):
    """Ошибка валидации (400)."""
    def __init__(self, message):
        super().__init__(message, HTTPStatus.BAD_REQUEST)


class NotFoundError(APIError):
    """Объект не найден (404)."""
    def __init__(self, message):
        super().__init__(message, HTTPStatus.NOT_FOUND)