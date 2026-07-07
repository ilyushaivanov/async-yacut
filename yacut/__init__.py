from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from .error_handlers import (bad_request, handle_api_error, internal_error,
                             method_not_allowed, not_found,
                             unsupported_media_type)
from .exceptions import APIError
from .settings import Config

db = SQLAlchemy()


def create_app():
    app = Flask(
        __name__,
        template_folder='../html',
        static_folder='../html',
        static_url_path=''
    )
    app.config.from_object(Config)

    db.init_app(app)

    from . import views
    app.register_blueprint(views.bp)

    from . import api_views
    app.register_blueprint(api_views.api_bp, url_prefix='/api')

    with app.app_context():
        db.create_all()

    app.register_error_handler(APIError, handle_api_error)
    app.register_error_handler(400, bad_request)
    app.register_error_handler(404, not_found)
    app.register_error_handler(405, method_not_allowed)
    app.register_error_handler(415, unsupported_media_type)
    app.register_error_handler(500, internal_error)

    return app


app = create_app()
