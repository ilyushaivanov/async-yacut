class APIError(Exception):
    """Базовое исключение для API‑ошибок."""
    def __init__(self, message, status_code):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ValidationError(APIError):
    """Ошибка валидации (400)."""
    def __init__(self, message):
        super().__init__(message, 400)


class NotFoundError(APIError):
    """Объект не найден (404)."""
    def __init__(self, message):
        super().__init__(message, 404)


class MethodNotAllowedError(APIError):
    """Неподдерживаемый метод (405)."""
    def __init__(self, message):
        super().__init__(message, 405)


class UnsupportedMediaError(APIError):
    """Некорректный формат запроса (415) -> 400."""
    def __init__(self, message):
        super().__init__(message, 400)