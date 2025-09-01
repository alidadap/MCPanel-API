from flask import jsonify
from database import session , Users
from Decorators import token_check, access_required, set_body
from ..server import storage
import bcrypt


@set_body
def get_users():
    users = session.query(Users).all()
    users_dict = []
    for user in users:
        users_dict.append({
            "id" : user.id,
            "username" : user.username,
            "email" : user.email,
            "access" : user.access
        })
    return jsonify({"users":users_dict})

@set_body
def add_user():
    condition_ok : bool = (
            storage['body'].get('user') and
            storage['body'].get('pass') and
            storage['body'].get('confirm') and
            storage['body'].get('access') and
            storage['body'].get('email') and
            not session.query(Users).filter_by(username=storage['body'].get('user'), password=storage['body'].get('pass'),access=storage['body'].get('access'),email=storage['body'].get('email')).first() and
            storage['body'].get('pass') == storage['body'].get('confirm')
        )
    if condition_ok:    
        hashed_password = bcrypt.hashpw(storage['body'].get('pass').encode(), storage['key']).decode()
        new_user = Users(username=storage['body'].get('user'), password=hashed_password,access=storage['body'].get('access'),email=storage['body'].get('email')) # type: ignore
        session.add(new_user)
        session.commit()
        return jsonify({"alert":"successful!"})
    else:
        return jsonify({"alert":"somethings is wrong!"})

@set_body
def update_user():
    id = int(storage['body'].get('id'))
    user = session.query(Users).get(id)
    
    condition_ok : bool = (
            storage['body'].get('user') and
            storage['body'].get('pass') and
            storage['body'].get('confirm') and
            storage['body'].get('access') and
            storage['body'].get('email') and
            storage['body'].get('pass') == storage['body'].get('confirm')
        )
    if condition_ok:    
        hashed_password = bcrypt.hashpw(storage['body'].get('pass').encode(), storage['key']).decode()
        user.username = storage['body'].get('user')
        user.password = hashed_password
        user.access = storage['body'].get('access')
        user.email = storage['body'].get('email')
        session.commit()
        return jsonify({"alert":"successful!"})
    else:
        return jsonify({"alert":"somethings is wrong!"})
@set_body
def remove_user():
    if storage['body'].get('id'):
        user = session.get(int(storage['body'].get('id'))) # type: ignore
        session.delete(user)
        session.commit()
        return jsonify({"alert":"user deleted!"})
    else:
        return jsonify({"data":None, "message":"Error"})