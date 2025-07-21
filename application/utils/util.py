# application/utils/util.py
import jwt
from datetime import datetime, timezone, timedelta
from functools import wraps
from flask import request,jsonify
from application.models import Customer
from application.models import db

SECRET_KEY = "my super secret, secret key"

def encode_token(customer_id): #using unique pieces of info to make our tokens user specific
    payload = {
        "exp" : datetime.now(timezone.utc) + timedelta(days=0 , hours= 1),  #Setting the expiration time to an hour past now
        "iat" : datetime.now(timezone.utc),  #Issued at
        "sub" : str(customer_id) #This needs to be a string or the token will be malformed and won't be able to be decoded.
                }
    
    token = jwt.encode(payload , SECRET_KEY , algorithm = 'HS256')

    return token


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token =None
         # Look for the token in the Authorization header
        if 'Authorization' in request.headers:
            print(request.headers)
            token = request.headers['Authorization'].split(" ")[1]
            print(token)
            if not token:
                return jsonify({"message": "Token is missing and Invalid Authorization header format!!."}), 400
            
            try:
                    # Decode the token
                data =jwt.decode(token , SECRET_KEY ,  algorithms = ['HS256'])
                print(data)
                print(f"Token to decode: '{token}'")
                customer_id = data['sub'] # Fetch the customer ID
                customer= db.session.get(Customer,customer_id)

                if not customer:
                    return jsonify({"message":"Invalid token — customer does not exist."}), 401
            except jwt.ExpiredSignatureError as e:
                return jsonify({'message': 'Token has expired!'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'message': 'Invalid token!'}), 401
            
            return f(customer_id, *args, **kwargs)
        
        else:
            return jsonify({"message": "You must be logged in to access this."}), 400
    
    return decorated

