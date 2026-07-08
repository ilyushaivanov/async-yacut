import asyncio

from flask import Blueprint, flash, redirect, render_template

from .exceptions import ValidationError
from .forms import FileForm, LinkForm
from .models import URLMap
from .services import upload_file_to_disk
from .settings import Config

bp = Blueprint('main', __name__)


@bp.route('/', methods=['GET', 'POST'])
def index():
    form = LinkForm()
    short_url = None

    if not form.validate_on_submit():
        return render_template('index.html', form=form, short_url=short_url)

    original = form.original_link.data
    custom_id = form.custom_id.data

    try:
        url_map = URLMap.create(original, custom_id if custom_id else None)
    except ValidationError as e:
        flash(e.message, 'danger')
    else:
        short_url = url_map.to_dict()['short_link']
        flash(f'Ваша короткая ссылка: {short_url}', 'success')

    return render_template('index.html', form=form, short_url=short_url)


@bp.route(f'/{Config.FILES_PREFIX}', methods=['GET', 'POST'])
def files_page():
    form = FileForm()

    if not form.validate_on_submit():
        return _render_files_page(form)

    files = form.files.data
    if not files:
        flash('Файлы не выбраны', 'danger')
        return _render_files_page(form)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        tasks = [upload_file_to_disk(f.read(), f.filename) for f in files]
        results = loop.run_until_complete(
            asyncio.gather(*tasks, return_exceptions=True)
        )
    finally:
        loop.close()

    for filename, result in zip([f.filename for f in files], results):
        if isinstance(result, Exception) or result is None:
            flash(f'Ошибка загрузки файла {filename}', 'danger')
            continue
        disk_link = result
        try:
            URLMap.create(disk_link, filename=filename)
        except ValidationError as e:
            flash(e.message, 'danger')
            continue
    flash('Файлы успешно загружены', 'success')
    return _render_files_page(form)


def _render_files_page(form):
    file_records = URLMap.query.filter(URLMap.filename.isnot(None)).all()
    uploaded_files = [rec.to_file_dict() for rec in file_records]
    return render_template(
        'files.html', form=form, uploaded_files=uploaded_files
    )


@bp.route('/<short_id>')
def redirect_to(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first_or_404()
    return redirect(url_map.original)