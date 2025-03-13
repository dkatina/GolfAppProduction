from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from app.blueprints.players.schemas import player_schema
from app.models import Account, Base, Player
from app.models import db
from . import account_bp
from .schemas import account_schema, accounts_schema
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.utils import encode_token, token_required

#login route
@account_bp.route('/login', methods=['POST'])
def login():
    try:
        account_data = account_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    with Session(db.engine) as session:
        account = session.query(Account).filter_by(email=account_data['email']).first()
        if account and check_password_hash(account.password, account_data['password']):
            token = encode_token(account.player.id)
            return jsonify({'token': token,
                            "message": "Successful Login",
                            "player": player_schema.dump(account.player)}), 200
        return jsonify({'error': 'Invalid username or password'}), 401

#Get ALl Accounts
@account_bp.route('/', methods=['GET'])
def get_accounts():
    with Session(db.engine) as session:
        accounts = session.query(Account).all()
        return jsonify(accounts_schema.dump(accounts))
    
#Get Account

@account_bp.route('/profile', methods=['GET'])
@token_required
def get_account():
    with Session(db.engine) as session:

        account = session.get(Player, request.user_id).account
        if account:
            return jsonify(account_schema.dump(account))
        return jsonify({'error': 'Account not found'}), 404

#Create Account
@account_bp.route('/', methods=['POST'])
def create_account():

    try:
        account_data = request.json
        new_account = Account(email=account_data['email'], password=generate_password_hash(account_data['password']))
        
        with Session(db.engine) as session:
            session.add(new_account)
            session.commit()
            new_player = Player(account_id=new_account.id, name=account_data['username'])
            session.add(new_player)
            session.commit()
            return jsonify({'message': "Account creation successful",
                           "Account": account_schema.dump(new_account)}), 201
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400

@account_bp.route('/', methods=['PUT'])
@token_required
def update_account():
    data = request.json
    with Session(db.engine) as session:
        account = session.get(Player, request.user_id).account
        if account:
            try:
                account = account_schema.load(data, instance=account, session=session, partial=True)
                session.commit()
                return jsonify(account_schema.dump(account))
            except ValidationError as err:
                return jsonify({'errors': err.messages}), 400
        return jsonify({'error': 'Account not found'}), 404

@account_bp.route('/<int:account_id>', methods=['DELETE'])
@token_required
def delete_account():
    with Session(db.engine) as session:
        account = session.get(Player, request.user_id).account
        if account:
            session.delete(account)
            session.commit()
            return jsonify({'message': 'Account deleted'})
        return jsonify({'error': 'Account not found'}), 404
