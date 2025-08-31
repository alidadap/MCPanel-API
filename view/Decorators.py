from flask import request, jsonify
from jwt import ExpiredSignatureError, decode, InvalidTokenError
from functools import wraps 
from flask_socketio import emit
from ..server import storage



    
def set_body(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        try:
            storage['body'] = dict(request.get_json())
        except:
            return 'ono'
        return f(*args, **kwargs)
    return wrapped

def socketio_token_check(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        token = request.args.get('token')  # Get token from query parameters
        if not token:
            emit('auth', {'alert': 'Token is required'}) # Send error to client
            return False  # Disconnect the client

        try:
            payload = decode(token, storage["key"], algorithms=["HS256"])
            user = payload.get('user')  # Assuming 'user' is in payload
            if not user:
                emit('auth', {'alert': 'Invalid token payload'})
                return False

            # Store the user in the storage for later use
            request.sid = request.sid  # type: ignore # Store storage ID
            request.user = user  # type: ignore # Store user

        except ExpiredSignatureError:
            emit('auth', {'alert': 'Token has expired'})
            return False
        except InvalidTokenError:
            emit('auth', {'alert': 'Token is invalid'})
            return False
        except Exception as e:
            emit('auth', {'alert': f'Token decoding failed: {e}'})
            return False
        return f(*args, **kwargs)
    return wrapped


# Token checker
def token_check(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        # Get token from cookies or JSON request
        
        token = request.cookies.get('token')
        if not token:
            token = request.form.get('token')
            if not token:
                token = dict(request.json).get('token') # type: ignore
                if not token:
                    return jsonify({'alert': 'Token is required'})
        try:
            # Decode token using the secret key
            payload = decode(token, storage["key"], algorithms=["HS256"])
            print(payload)
        except ExpiredSignatureError:
            return jsonify({'alert': 'Token has expired'})
        except InvalidTokenError:
            return jsonify({'alert': 'Token is invalid'})
        return func(*args, **kwargs)
    return decorated

def socket_access_required(required_access):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            try:
                token = request.args.get('token')
                if not token:
                    print('token req')
                    return False
                
                payload = decode(token, storage["key"], algorithms=["HS256"])
                user_access = payload.get('access')
                
                print(required_access,' : ',user_access)
                if required_access not in user_access:
                    print('access deny')
                    return False
                
                return f(*args, **kwargs)
                
            except Exception as e:
                print(e)
                return False
        return wrapped
    return decorator

def access_required(required_access):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.cookies.get('token') or request.form.get('token') or (request.json and request.json.get('token'))
            if not token:
                return jsonify({'alert': 'Token is required'}), 401
            
            try:
                payload = decode(token, storage["key"], algorithms=["HS256"])
                user_access = payload.get('access')
                
                if str(required_access) not in user_access:
                    return jsonify({'alert': 'Access denied'}), 403
                    
            except Exception as e:
                return jsonify({'alert': str(e)}), 401
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator