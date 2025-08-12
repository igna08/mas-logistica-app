from celery import Celery
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
celery = Celery(__name__, broker='redis://redis:6379/0', backend='redis://redis:6379/0')
