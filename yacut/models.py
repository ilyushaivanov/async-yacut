import random
import string
from datetime import datetime

from flask import url_for

from . import db
from .exceptions import ValidationError
from .settings import Config


class URLMap(db.Model):
    """
    Модель для хранения соответствия между ссылками.
    """

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(Config.MAX_ORIGINAL_LENGTH), nullable=False)
    short = db.Column(
        db.String(Config.MAX_CUSTOM_ID_LENGTH),
        unique=True, nullable=False, index=True
    )
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    filename = db.Column(db.String(Config.MAX_ORIGINAL_LENGTH), nullable=True)

    def to_dict(self):
        """Возвращает словарь для API-ответа (создание короткой ссылки)."""
        return {
            'url': self.original,
            'short_link': url_for(
                'main.redirect_to', short_id=self.short, _external=True
            )
        }

    @staticmethod
    def generate_short_id(length=Config.SHORT_ID_LENGTH):
        """Генерирует случайную строку заданной длины из букв и цифр."""
        chars = string.ascii_letters + string.digits
        return ''.join(random.choices(chars, k=length))

    @staticmethod
    def _is_forbidden(short_id):
        """Проверяет, входит ли короткий идентификатор в список запрещённых."""
        return short_id in Config.FORBIDDEN_SHORT_NAMES

    @staticmethod
    def get_by_short(short_id):
        """Находит запись по короткому идентификатору."""
        return URLMap.query.filter_by(short=short_id).first()

    @staticmethod
    def get_unique_short_id(length=Config.SHORT_ID_LENGTH):
        """Генерирует уникальный короткий идентификатор."""
        while True:
            short_id = URLMap.generate_short_id(length)
            if URLMap._is_forbidden(short_id) or URLMap.get_by_short(short_id):
                continue
            return short_id

    @staticmethod
    def create(original, custom_id=None, filename=None):
        """
        Создаёт новую запись в БД.
        """
        if custom_id:
            if URLMap._is_forbidden(
                custom_id
            ) or URLMap.get_by_short(custom_id):
                raise ValidationError(
                    'Предложенный вариант короткой ссылки уже существует.'
                )
            short_id = custom_id
        else:
            short_id = URLMap.get_unique_short_id()

        url_map = URLMap(original=original, short=short_id, filename=filename)
        db.session.add(url_map)
        db.session.commit()
        return url_map
