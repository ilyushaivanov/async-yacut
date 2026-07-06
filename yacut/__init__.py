from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
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

    @app.errorhandler(404)
    def page_not_found(e):
        if request.path.startswith('/api/'):
            return jsonify({'message': 'Указанный id не найден'}), 404
        return render_template(
            'error.html', error_code=404, error_message='Страница не найдена'
        ), 404

    @app.errorhandler(500)
    def internal_error(e):
        if request.path.startswith('/api/'):
            return jsonify({'message': 'Внутренняя ошибка сервера'}), 500
        return render_template(
            'error.html',
            error_code=500,
            error_message='Внутренняя ошибка сервера'
        ), 500

    return app


app = create_app()