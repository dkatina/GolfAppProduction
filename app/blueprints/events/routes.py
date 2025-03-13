import re
from marshmallow import ValidationError
from sqlalchemy.orm import Session
from flask import request, jsonify
from app.blueprints.players.schemas import players_schema
from app.models import Event, Player, db, EventPlayers
from app.extensions import ma
from app.utils.utils import token_required
from .schemas import event_schema, events_schema, event_players_schema, event_player_schema
from . import event_bp

#GET ALL EVENTS
@event_bp.route('/', methods=['GET'])
def get_events():
    with Session(db.engine) as session:
        events = session.query(Event).all()
        return jsonify(events_schema.dump(events))
    
#GET SPECIFIC EVENT
@event_bp.route('/<int:event_id>', methods=['GET'])
def get_event(event_id):
    with Session(db.engine) as session:
        event = session.get(Event, event_id)
        if event:
            return jsonify(event_schema.dump(event))
        return jsonify({'error': 'Event not found'}), 404

#CREATE AN EVENT
@event_bp.route('/', methods=['POST'])
@token_required
def create_event():
    data = request.json
    try:
        data['owner_id'] = request.user_id
        new_event = event_schema.load(data)
        with Session(db.engine) as session:
            session.add(new_event)
            session.commit()
            new_event_player = EventPlayers(player_id=request.user_id, event_id=new_event.id, event_score=0)
            session.add(new_event_player)
            session.commit()
            return jsonify(event_schema.dump(new_event)), 201
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400

#UPDATE EVENT
@event_bp.route('/<int:event_id>', methods=['PUT'])
@token_required
def update_event(event_id):
    data = request.json
    with Session(db.engine) as session:
        event = session.get(Event, event_id)
        if event:
            if event.owner_id != request.user_id:
                return jsonify({'error': 'Unauthorized'}), 403
            try:
                event = event_schema.load(data, instance=event, partial=True)
                session.commit()
                return jsonify(event_schema.dump(event))
            except ValidationError as err:
                return jsonify({'errors': err.messages}), 400
        return jsonify({'error': 'Event not found'}), 404

#DELETE EVENT
@event_bp.route('/<int:event_id>', methods=['DELETE'])
@token_required
def delete_event(event_id):
    with Session(db.engine) as session:
        event = session.get(Event, event_id)
        if event:
            if event.owner_id != request.user_id:
                return jsonify({'error': 'Unauthorized'}), 403
            session.delete(event)
            session.commit()
            return jsonify({'message': 'Event deleted'})
        return jsonify({'error': 'Event not found'}), 404
    

#MY EVENTS
@event_bp.route('/my-events', methods=['GET'])
@token_required
def get_my_events():
    with Session(db.engine) as session:
        my_events = session.query(Event).join(Event.event_players).filter_by(player_id=request.user_id).all()
        return jsonify(events_schema.dump(my_events))
    
#Event Score
@event_bp.route('/<int:event_id>/my-score', methods=['GET'])
@token_required
def my_event_score(event_id):
    with Session(db.engine) as session:
        my_event = session.query(EventPlayers).filter_by(player_id=request.user_id, event_id=event_id).first()
        print(my_event)
        return jsonify(event_player_schema.dump(my_event))
    

#EVENT PLAYERS
@event_bp.route('/<int:event_id>/players', methods=['GET'])
@token_required
def event_players(event_id):
    with Session(db.engine) as session:
        event = session.get(Event, event_id)
        event_players = session.query(EventPlayers).filter_by(event_id=event_id).all()
        return jsonify({"players": event_players_schema.dump(event_players),
                        "event": event_schema.dump(event),
                        "invited": players_schema.dump(event.invites)}),200
    
#INVITE PLAYER
@event_bp.route('/<int:event_id>/invite-player/<int:player_id>', methods=["PUT"])
@token_required
def invite_player(event_id, player_id):
    with Session(db.engine) as session:
        event = session.get(Event, event_id)
        player = session.get(Player, player_id)
        print(player)
        if event and player:
            if event.owner_id == int(request.user_id):
                if player not in event.invites:
                    event.invites.append(player)
                    session.commit()
                    return jsonify({"message": f"Successfully invited {player.name}"})
                else:
                    return jsonify({"Error": "player already invited."}), 400
            else:
                return jsonify({"Error": "You must be the event owner to invite players"}), 400
        else:
            return jsonify({"Error": "Invalid event_id or player_id."}), 400
        


    
@event_bp.route('/<int:event_id>/leaderboard', methods=['GET'])
@token_required
def leaderboard(event_id):
    with Session(db.engine) as session:
        event = session.get(Event, event_id)
        event_players = session.query(EventPlayers).filter_by(event_id=event_id).order_by(EventPlayers.event_score).all()[::-1]
        return jsonify({"players": event_players_schema.dump(event_players),
                        "event": event_schema.dump(event)}),200
    