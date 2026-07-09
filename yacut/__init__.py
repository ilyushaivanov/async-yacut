from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from .error_handlers import init_error_handlers
from .settings import Config

db = SQLAlchemy()


def create_app():
    """
    Создание приложения Flask.
    """
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

    init_error_handlers(app)

    return app


app = create_app()
