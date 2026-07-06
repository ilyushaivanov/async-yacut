import random
import string
from datetime import datetime

from yacut import db


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(256), nullable=False)
    short = db.Column(db.String(16), unique=True, nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    filename = db.Column(db.String(256), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'original': self.original,
            'short': self.short,
            'timestamp': self.timestamp.isoformat()
        }


def generate_short_id(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


def get_unique_short_id(length=6):
    while True:
        short_id = generate_short_id(length)
        if not URLMap.query.filter_by(short=short_id).first():
            return short_id