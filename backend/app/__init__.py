from flask import Flask
from .config import config
from .extensions import db, migrate, jwt, celery

def create_app(config_name='default'):
    """
    Application factory function.
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Configure Celery
    celery.conf.update(
        broker_url=app.config['CELERY_BROKER_URL'],
        result_backend=app.config['CELERY_RESULT_BACKEND']
    )
    celery.conf.update(app.config)

    # Register Blueprints
    from .api.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from .api.vehiculos import bp as vehiculos_bp
    app.register_blueprint(vehiculos_bp)

    from .api.recorridos import bp as recorridos_bp
    app.register_blueprint(recorridos_bp)

    from .api.controles import bp as controles_bp
    app.register_blueprint(controles_bp)

    from .api.uploads import bp as uploads_bp
    app.register_blueprint(uploads_bp)

    # Shell context for flask cli
    @app.shell_context_processor
    def make_shell_context():
        return dict(app=app, db=db)

    return app
