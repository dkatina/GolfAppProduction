from flask import Flask, render_template
from .extensions import ma
from .models import db
from .blueprints.accounts import account_bp
from .blueprints.players import player_bp
from .blueprints.events import event_bp
from flask_cors import CORS


def create_app(config_name):
    app = Flask(__name__, static_folder="dist/assets", template_folder="dist")
    app.config.from_object(f'config.{config_name}')

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    CORS(app)

    app.register_blueprint(account_bp, url_prefix="/accounts")
    app.register_blueprint(player_bp, url_prefix="/players")
    app.register_blueprint(event_bp, url_prefix="/events")

    # CLI commands
    @app.route('/')
    def index():
        return render_template('index.html')

    return app