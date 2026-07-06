from urllib.parse import quote

import aiohttp

from .settings import Config


async def get_upload_url(session, path):
    encoded_path = quote(path, safe='')
    url = (
        f'https://cloud-api.yandex.net/v1/disk/resources/upload?'
        f'path={encoded_path}'
    )
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
        download_url = (
            f'https://cloud-api.yandex.net/v1/disk/resources/download?'
            f'path={quote(path, safe="")}'
        )
        headers = {'Authorization': f'OAuth {Config.DISK_TOKEN}'}
        async with session.get(download_url, headers=headers) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            return data.get('href')