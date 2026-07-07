import re
from http import HTTPStatus
from flask import Blueprint, jsonify, request
from .models import URLMap
from .settings import Config
from .exceptions import ValidationError, NotFoundError

api_bp = Blueprint('api', __name__)


@api_bp.route('/id/', methods=['POST'])
def create_short_link():
    data = request.get_json(silent=True)
    if data is None:
        raise ValidationError('Отсутствует тело запроса')
    if 'url' not in data:
        raise ValidationError('"url" является обязательным полем!')
    original = data['url']
    custom_id = data.get('custom_id', '')

    if not original.startswith(('http://', 'https://')):
        raise ValidationError('Некорректный URL')

    if custom_id:
        if len(custom_id) > Config.MAX_CUSTOM_ID_LENGTH:
            raise ValidationError(
                'Указано недопустимое имя для короткой ссылки'
            )
        if not re.match(r'^[a-zA-Z0-9]+$', custom_id):
            raise ValidationError(
                'Указано недопустимое имя для короткой ссылки'
            )

    url_map = URLMap.create(original, custom_id if custom_id else None)
    return jsonify(url_map.to_dict()), HTTPStatus.CREATED


@api_bp.route('/id/<short_id>/', methods=['GET'])
def get_original_link(short_id):
    url_map = URLMap.get_by_short(short_id)
    if url_map is None:
        raise NotFoundError('Указанный id не найден')
    return jsonify({'url': url_map.original}), HTTPStatus.OK
