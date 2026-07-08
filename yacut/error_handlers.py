from http import HTTPStatus

from flask import jsonify, render_template, request


def bad_request(e):
    if request.path.startswith('/api/'):
        return jsonify(
            {'message': 'Некорректный запрос'}
        ), HTTPStatus.BAD_REQUEST
    return render_template(
        'error.html', error_code=HTTPStatus.BAD_REQUEST,
        error_message='Некорректный запрос'
    ), HTTPStatus.BAD_REQUEST


def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify(
            {'message': 'Указанный id не найден'}
        ), HTTPStatus.NOT_FOUND
    return render_template(
        'error.html', error_code=HTTPStatus.NOT_FOUND,
        error_message='Страница не найдена'
    ), HTTPStatus.NOT_FOUND


def internal_error(e):
    if request.path.startswith('/api/'):
        return jsonify(
            {'message': 'Внутренняя ошибка сервера'}
        ), HTTPStatus.INTERNAL_SERVER_ERROR
    return render_template(
        'error.html', error_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        error_message='Внутренняя ошибка сервера'
    ), HTTPStatus.INTERNAL_SERVER_ERROR


def handle_validation_error(e):
    """Обработчик кастомного исключения ValidationError."""
    return jsonify(e.to_dict()), e.status_code


def handle_not_found_error(e):
    """Обработчик кастомного исключения NotFoundError."""
    return jsonify(e.to_dict()), e.status_code