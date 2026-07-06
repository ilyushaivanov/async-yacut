import asyncio
import aiohttp
from flask import Blueprint, render_template, redirect, url_for, flash
from .forms import LinkForm, FileForm
from .models import URLMap, get_unique_short_id
from . import db
from .settings import Config

bp = Blueprint('main', __name__)


async def get_upload_url(session, path):
    url = f'https://cloud-api.yandex.net/v1/disk/resources/upload?path={path}'
    headers = {'Authorization': f'OAuth {Config.DISK_TOKEN}'}
    async with session.get(url, headers=headers) as resp:
        if resp.status != 200:
            return None
        data = await resp.json()
        return data.get('href')


async def upload_file_to_disk(file_data, filename):
    path = f'/yacut/{filename}'
    async with aiohttp.ClientSession() as session:
        upload_url = await get_upload_url(session, path)
        if not upload_url:
            return None
        async with session.put(upload_url, data=file_data) as resp:
            if resp.status not in (200, 201):
                return None
        publish_url = (
            f'https://cloud-api.yandex.net/v1/disk/resources/publish?path='
            f'{path}'
        )
        headers = {'Authorization': f'OAuth {Config.DISK_TOKEN}'}
        async with session.put(publish_url, headers=headers) as resp:
            if resp.status not in (200, 201):
                return None
        download_url = (
            f'https://cloud-api.yandex.net/v1/disk/resources/download?path='
            f'{path}'
        )
        headers = {'Authorization': f'OAuth {Config.DISK_TOKEN}'}
        async with session.get(download_url, headers=headers) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            return data.get('href')


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
    uploaded_files = []
    if form.validate_on_submit():
        files = form.files.data
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tasks = [upload_file_to_disk(f.read(), f.filename) for f in files]
        results = loop.run_until_complete(asyncio.gather(*tasks))
        loop.close()

        for filename, disk_link in zip([f.filename for f in files], results):
            if disk_link is None:
                flash(f'Ошибка загрузки файла {filename}', 'danger')
                continue
            short_id = get_unique_short_id()
            url_map = URLMap(original=disk_link, short=short_id)
            db.session.add(url_map)
            db.session.commit()
            short_url = url_for(
                'main.redirect_to', short_id=short_id, _external=True
            )
            uploaded_files.append({'name': filename, 'short_url': short_url})
        if uploaded_files:
            flash('Файлы успешно загружены', 'success')
    return render_template(
        'files.html', form=form, uploaded_files=uploaded_files
    )


@bp.route('/<short_id>')
def redirect_to(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first_or_404()
    return redirect(url_map.original)