import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URI'
    ) or 'sqlite:///yacut.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DISK_TOKEN = os.environ.get('DISK_TOKEN')
    MAX_CUSTOM_ID_LENGTH = 16
    SHORT_ID_LENGTH = 6
    WTF_CSRF_ENABLED = False
    WTF_CSRF_CHECK_DEFAULT = False