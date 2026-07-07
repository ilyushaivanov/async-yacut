from flask_wtf import FlaskForm
from wtforms import MultipleFileField, StringField, SubmitField
from wtforms.validators import URL, DataRequired, Length, Optional, Regexp

from .settings import Config


class LinkForm(FlaskForm):
    original_link = StringField(
        'Длинная ссылка',
        validators=[
            DataRequired(message='Обязательное поле'),
            URL(message='Некорректный URL'),
            Length(max=Config.MAX_ORIGINAL_LENGTH,
                   message=f'Не более {Config.MAX_ORIGINAL_LENGTH} символов')
        ]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Optional(),
            Length(max=Config.MAX_CUSTOM_ID_LENGTH,
                   message=f'Не более {Config.MAX_CUSTOM_ID_LENGTH} символов'),
            Regexp(r'^[a-zA-Z0-9]+$',
                   message='Допустимы только латинские буквы и цифры.')
        ]
    )
    submit = SubmitField('Создать')


class FileForm(FlaskForm):
    files = MultipleFileField('Выберите файлы', validators=[DataRequired()])
    submit = SubmitField('Загрузить')
