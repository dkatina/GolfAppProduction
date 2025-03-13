
from app.models import Event, EventPlayers
from app.extensions import ma
from marshmallow import fields


class EventSchema(ma.SQLAlchemyAutoSchema):
    owner = fields.Nested("PlayerSchema")
    class Meta:
        model = Event
        include_fk = True
        load_instance = True
        include_relationships = True

event_schema = EventSchema()
events_schema = EventSchema(many=True)

class EventPlayerSchema(ma.SQLAlchemyAutoSchema):
    player = fields.Nested("PlayerSchema")
    class Meta:
        model = EventPlayers
        fields = ("player", "event_score")

event_players_schema = EventPlayerSchema(many=True)
event_player_schema = EventPlayerSchema()
