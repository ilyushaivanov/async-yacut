import aiohttp

from .settings import Config


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
            f'https://cloud-api.yandex.net/v1/disk/resources/publish?'
            f'path={path}'
        )
        headers = {'Authorization': f'OAuth {Config.DISK_TOKEN}'}
        async with session.put(publish_url, headers=headers) as resp:
            if resp.status not in (200, 201):
                return None
        download_url = (
            f'https://cloud-api.yandex.net/v1/disk/resources/download?'
            f'path={path}'
        )
        async with session.get(download_url, headers=headers) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            return data.get('href')
