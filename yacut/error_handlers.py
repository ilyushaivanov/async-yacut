from http import HTTPStatus

from flask import jsonify, render_template, request

from .exceptions import NotFoundError, ValidationError


def init_error_handlers(app):
    """Регистрирует все обработчики ошибок в приложении."""

    @app.errorhandler(400)
    def bad_request(e):
        """Обработчик ошибки 400 (Bad Request)."""
        if request.path.startswith('/api/'):
            return jsonify(
                {'message': 'Некорректный запрос'}
            ), HTTPStatus.BAD_REQUEST
        return render_template(
            'error.html', error_code=HTTPStatus.BAD_REQUEST,
            error_message='Некорректный запрос'
        ), HTTPStatus.BAD_REQUEST

    @app.errorhandler(404)
    def not_found(e):
        """Обработчик ошибки 404 (Not Found)."""
        if request.path.startswith('/api/'):
            return jsonify(
                {'message': 'Указанный id не найден'}
            ), HTTPStatus.NOT_FOUND
        return render_template(
            'error.html', error_code=HTTPStatus.NOT_FOUND,
            error_message='Страница не найдена'
        ), HTTPStatus.NOT_FOUND

    @app.errorhandler(500)
    def internal_error(e):
        """Обработчик ошибки 500 (Internal Server Error)."""
        if request.path.startswith('/api/'):
            return jsonify(
                {'message': 'Внутренняя ошибка сервера'}
            ), HTTPStatus.INTERNAL_SERVER_ERROR
        return render_template(
            'error.html', error_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            error_message='Внутренняя ошибка сервера'
        ), HTTPStatus.INTERNAL_SERVER_ERROR

    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        """Обработчик кастомного исключения ValidationError."""
        return jsonify(e.to_dict()), e.status_code

    @app.errorhandler(NotFoundError)
    def handle_not_found_error(e):
        """Обработчик кастомного исключения NotFoundError."""
        return jsonify(e.to_dict()), e.status_code