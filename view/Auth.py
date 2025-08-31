from jwt import  encode 
from datetime import datetime, timedelta 
from flask import request, jsonify 
import bcrypt
from database import session , Users
from ..server import storage



def login():

    # Try to get body from frount
    try:
        body = dict(request.json) # type: ignore
        password = bcrypt.hashpw(body['pass'].encode(),storage['key']).decode() # type: ignore
        user = session.query(Users).filter_by(username=body['user']).first() # type: ignore
        print(user)
    except Exception as error:
        print(error)
        return jsonify({"alert": 'Failed! Check the Console on Backend'})
        
    # Check username and password validity
    if user.password == password:

        # Generate JWT token
        token = encode({
            "user": body['user'], # type: ignore
            "access": user.access,
            "exp": datetime.utcnow() + timedelta(minutes=30)
            }, storage["key"], algorithm="HS256")
            
        # Create response with HttpOnly cookie
        resp = jsonify({'alert': 'Login successful', 'token': token,'access': user.access})
        return resp
    # If user not in the database
    else:

        return jsonify({'alert': 'Invalid username or password', 'token': None})