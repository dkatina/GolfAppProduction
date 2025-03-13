from app.models import Player
from app.extensions import ma

class PlayerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Player
   

player_schema = PlayerSchema()
players_schema = PlayerSchema(many=True)