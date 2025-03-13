from flask import Blueprint

player_bp = Blueprint('players', __name__)


from . import routes