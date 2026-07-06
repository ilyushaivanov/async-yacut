import asyncio
from flask import Blueprint, render_template, redirect, url_for, flash
from .forms import LinkForm, FileForm
from .models import URLMap, get_unique_short_id
from . import db
from .services import upload_file_to_disk

bp = Blueprint('main', __name__)


@bp.route('/', methods=['GET', 'POST'])
def index():
    form = LinkForm()
    short_url = None
    if form.validate_on_submit():
        original = form.original_link.data
        custom_id = form.custom_id.data
        short_id = custom_id if custom_id else get_unique_short_id()
        existing = URLMap.query.filter_by(short=short_id).first()
        if existing:
            flash(
                'Предложенный вариант короткой ссылки уже существует.',
                'danger'
            )
        else:
            url_map = URLMap(original=original, short=short_id)
            db.session.add(url_map)
            db.session.commit()
            short_url = url_for(
                'main.redirect_to', short_id=short_id, _external=True
            )
            flash(f'Ваша короткая ссылка: {short_url}', 'success')
    return render_template('index.html', form=form, short_url=short_url)


@bp.route('/files', methods=['GET', 'POST'])
def files_page():
    form = FileForm()

    if form.validate_on_submit():
        files = form.files.data
        if files:
            tasks = [upload_file_to_disk(f.read(), f.filename) for f in files]

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
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
                short_id = get_unique_short_id()
                url_map = URLMap(
                    original=disk_link,
                    short=short_id,
                    filename=filename
                )
                db.session.add(url_map)
                db.session.commit()

            flash('Файлы успешно загружены', 'success')
        else:
            flash('Файлы не выбраны', 'danger')

    file_records = URLMap.query.filter(URLMap.filename.isnot(None)).all()
    uploaded_files = []
    for rec in file_records:
        short_url = url_for(
            'main.redirect_to', short_id=rec.short, _external=True
        )
        uploaded_files.append({
            'name': rec.filename,
            'short_url': short_url
        })

    return render_template(
        'files.html',
        form=form,
        uploaded_files=uploaded_files
    )


@bp.route('/<short_id>')
def redirect_to(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first_or_404()
    return redirect(url_map.original)