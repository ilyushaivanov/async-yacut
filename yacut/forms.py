import re

from flask_wtf import FlaskForm
from wtforms import MultipleFileField, StringField, SubmitField
from wtforms.validators import (URL, DataRequired, Length, Optional,
                                ValidationError)

from .models import URLMap
from .settings import Config


class LinkForm(FlaskForm):
    original_link = StringField(
        'Длинная ссылка',
        validators=[
            DataRequired(message='Обязательное поле'),
            URL(message='Некорректный URL')
        ]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Optional(),
            Length(
                max=Config.MAX_CUSTOM_ID_LENGTH, message='Не более 16 символов'
            )
        ]
    )
    submit = SubmitField('Создать')

    def validate_custom_id(self, field):
        if field.data:
            if field.data.lower() == 'files':
                raise ValidationError(
                    'Предложенный вариант короткой ссылки уже существует.'
                )
            if not re.match(r'^[a-zA-Z0-9]+$', field.data):
                raise ValidationError(
                    'Допустимы только латинские буквы и цифры.'
                )
            if URLMap.query.filter_by(short=field.data).first():
                raise ValidationError(
                    'Предложенный вариант короткой ссылки уже существует.'
                )


class FileForm(FlaskForm):
    files = MultipleFileField('Выберите файлы', validators=[DataRequired()])
    submit = SubmitField('Загрузить')