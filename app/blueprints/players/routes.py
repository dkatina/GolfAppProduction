from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from marshmallow import ValidationError
from app.blueprints.events.schemas import  events_schema, event_player_schema
from app.models import Event, EventPlayers, Player, db
from app.extensions import ma
from app.utils.utils import token_required
from . import player_bp
from .schemas import player_schema, players_schema

#Get Players
@player_bp.route('/', methods=['GET'])
def get_players():
    with Session(db.engine) as session:
        players = session.query(Player).all()
        return jsonify(players_schema.dump(players))

#Get Specific Player
@player_bp.route('/<int:player_id>', methods=['GET'])
def get_player(player_id):
    with Session(db.engine) as session:
        player = session.get(Player, player_id)
        if player:
            return jsonify(player_schema.dump(player))
        return jsonify({'error': 'Player not found'}), 404


#Update Player
@player_bp.route('/', methods=['PUT'])
@token_required
def update_player():
    try:
        player_data = player_schema.load(request.json)
    except ValidationError as err:
                return jsonify({'errors': err.messages}), 400
    with Session(db.engine) as session:
        player = session.get(Player, request.user_id)
        
        if player:
            for field, value in player_data.items():
             setattr(player, field, value)
                
            session.commit()
            return jsonify(player_schema.dump(player))
            
        return jsonify({'error': 'Player not found'}), 404
    
#search player by name
@player_bp.route('/search', methods=['GET'])
def search_players():
    name_query = request.args.get('name').replace('-', ' ')

    if not name_query:
        return jsonify({'error': 'Name query parameter is required'}), 400

    with Session(db.engine) as session:
        players = session.query(Player).filter(Player.name.ilike(f"%{name_query}%")).all()
        return jsonify(players_schema.dump(players))

#MY INVITES    
@player_bp.route("/my-invites", methods=['GET'])
@token_required
def my_invites():
    with Session(db.engine) as session:
        return events_schema.jsonify(session.get(Player, request.user_id).invites), 200
    
#ACCEPT INVITE
@player_bp.route("/accept-invite/<int:event_id>", methods=['PUT']) 
@token_required
def accept_invite(event_id):
    with Session(db.engine) as session:
        player = session.get(Player, request.user_id)
        event = session.get(Event, event_id)

        if player and event:
            if event in player.invites:
                event_player = EventPlayers(player_id=player.id, event_id=event.id, event_score=0)
                session.add(event_player)
                player.invites.remove(event)
                session.commit()
                return jsonify({"message": f"Invite to {event.title} Accepted"}), 200
            else:
                return jsonify({"error": f"You are not invited to this event"}), 400
        else:
            return jsonify({"error": f"Invalid event_id"}), 400

#DECLINE INVITE       
@player_bp.route("/decline-invite/<int:event_id>", methods=['DELETE']) 
@token_required
def decline_invite(event_id):
    with Session(db.engine) as session:
        player = session.get(Player, request.user_id)
        event = session.get(Event, event_id)

        if player and event:
            if event in player.invites:
                player.invites.remove(event)
                session.commit()
                return jsonify({"message": f"Invite to {event.title} Declined."}), 200
            else:
                return jsonify({"error": f"You are not invited to this event."}), 400
        else:
            return jsonify({"error": f"Invalid event_id"}), 400
        

@player_bp.route("/add-event-point/<int:event_id>", methods=["PUT"])
@token_required
def add_event_point(event_id):
    with Session(db.engine) as session:
        player = session.get(Player, request.user_id)
        player_event = session.query(EventPlayers).filter_by(player_id=player.id, event_id = event_id).first()
        if player and player_event:
            player_event.event_score += 1
            session.commit()
            return event_player_schema.jsonify(player_event), 200
        else:
            return jsonify({"error": "Invalid player_id or event_id"})
        
@player_bp.route("/remove-event-point/<int:event_id>", methods=["DELETE"])
@token_required
def remove_event_point(event_id):
    with Session(db.engine) as session:
        player = session.get(Player, request.user_id)
        player_event = session.query(EventPlayers).filter_by(player_id=player.id, event_id = event_id).first()
        if player and player_event and player_event.event_score > 0:
            player_event.event_score -= 1
            session.commit()
            return event_player_schema.jsonify(player_event), 200
        else:
            return jsonify({"error": "Invalid player_id or event_id or score at 0"})




