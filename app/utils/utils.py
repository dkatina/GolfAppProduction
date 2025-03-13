
from datetime import datetime, timezone, timedelta
from functools import wraps
from jose import jwt
import jose
from flask import request, jsonify
import datetime

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

# Function to encode a token
# app/utils/util.py
from datetime import datetime, timedelta, timezone
from jose import jwt
import jose

SECRET_KEY = "a super secret, secret key"

def encode_token(user_id): #using unique pieces of info to make our tokens user specific
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0,hours=1), #Setting the expiration time to an hour past now
        'iat': datetime.now(timezone.utc), #Issued at
        'sub':  str(user_id)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

# Decorator to require token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Look for the token in the Authorization heade
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # Decode the token
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.user_id = data['sub']
        except jose.exceptions.ExpiredSignatureError:
             return jsonify({'message': 'Token has expired!'}), 401
        except jose.exceptions.JWTError:
             return jsonify({'message': 'Invalid token!'}), 401

        return f(*args, **kwargs)

    return decorated