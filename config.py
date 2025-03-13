

import os


class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'
    DEBUG = True
    FLASK_APP = "app.py"


class ProductionConfig:
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///app.db'