from flask import Blueprint, request, jsonify, url_for
from .models import URLMap, get_unique_short_id
from . import db
from .settings import Config
import re

api_bp = Blueprint('api', __name__)


@api_bp.errorhandler(400)
def bad_request(e):
    return jsonify({'message': 'Некорректный запрос'}), 400


@api_bp.errorhandler(404)
def not_found(e):
    return jsonify({'message': 'Ресурс не найден'}), 404


@api_bp.errorhandler(405)
def method_not_allowed(e):
    return jsonify({'message': 'Метод не разрешён'}), 405


@api_bp.errorhandler(415)
def unsupported_media_type(e):
    return jsonify({'message': 'Отсутствует поле url'}), 400


@api_bp.route('/id/', methods=['POST'])
def create_short_link():
    data = request.get_json(silent=True)
    if data is None or 'url' not in data:
        return jsonify({'message': 'Отсутствует поле url'}), 400

    original = data['url']
    custom_id = data.get('custom_id', '')

    if not original.startswith(('http://', 'https://')):
        return jsonify({'message': 'Некорректный URL'}), 400

    if custom_id:
        if len(custom_id) > Config.MAX_CUSTOM_ID_LENGTH:
            return jsonify({'message': 'custom_id не более 16 символов'}), 400
        if custom_id == 'files':
            return jsonify({'message': 'Имя занято'}), 400
        if not re.match(r'^[a-zA-Z0-9]+$', custom_id):
            return jsonify({'message': 'Только латинские буквы и цифры'}), 400
        if URLMap.query.filter_by(short=custom_id).first():
            return jsonify({'message': 'Имя занято'}), 400
        short_id = custom_id
    else:
        short_id = get_unique_short_id()

    url_map = URLMap(original=original, short=short_id)
    db.session.add(url_map)
    db.session.commit()
    short_url = url_for('main.redirect_to', short_id=short_id, _external=True)

    return jsonify({
        'url': original,
        'short_link': short_url,
        'short_id': short_id
    }), 201


@api_bp.route('/id/<short_id>/', methods=['GET'])
def get_original_link(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    if not url_map:
        return jsonify({'message': 'Ссылка не найдена'}), 404
    return jsonify({'url': url_map.original})