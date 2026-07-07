from http import HTTPStatus

from flask import jsonify, render_template, request


def handle_api_error(e):
    """Обработчик всех API‑исключений."""
    if request.path.startswith('/api/'):
        return jsonify({'message': e.message}), e.status_code
    return render_template(
        'error.html', error_code=e.status_code,
        error_message=e.message), e.status_code


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


def method_not_allowed(e):
    return jsonify(
        {'message': 'Метод не разрешён'}
    ), HTTPStatus.METHOD_NOT_ALLOWED


def unsupported_media_type(e):
    return jsonify(
        {'message': 'Отсутствует тело запроса'}
    ), HTTPStatus.BAD_REQUEST


def internal_error(e):
    if request.path.startswith('/api/'):
        return jsonify(
            {'message': 'Внутренняя ошибка сервера'}
        ), HTTPStatus.INTERNAL_SERVER_ERROR
    return render_template(
        'error.html', error_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        error_message='Внутренняя ошибка сервера'
    ), HTTPStatus.INTERNAL_SERVER_ERROR