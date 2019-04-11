from flask import request
from werkzeug.exceptions import Unauthorized, InternalServerError
from nightowl.app import db
from flask_restful import Resource
import jwt
import bcrypt
from datetime import datetime, timedelta
import time
import uuid

from nightowl.app import db
from ..auth.authentication import token_required
from ..auth.authentication import app
from nightowl.models.users import Users
from nightowl.models.groupMember import GroupMember
from nightowl.models.group import Group
from nightowl.models.usersLogs import UsersLogs
from nightowl.models.permission import Permission



class login(Resource):
    def post(self):
        token = ''
        datetime_now = datetime.strptime(datetime.strftime(datetime.today(),'%Y-%m-%d %I:%M %p'),'%Y-%m-%d %I:%M %p')
        public_id = str(uuid.uuid4())
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
            try:
                data = jwt.decode(token, app.config['SECRET_KEY'])
                user_log = UsersLogs.query.filter_by(username = data['username'], public_id = data['public_id'])
                user = Users.query.filter_by(username = data['username'])
                if user.count() == 0:
                    raise Unauthorized()
                if user_log.count() == 0:
                    return {"message": "user already logout"}
                elif user_log.first().status != "active":
                    return {"message": "user already logout"}
                token = jwt.encode({'username': data['username'], 'public_id' : public_id, 'exp': datetime_now + timedelta(days = 1)}, app.config['SECRET_KEY'])
                token = token.decode('UTF-8')
                userType = get_user_type(user.first().id)
                return {"token": token, 'userType': userType}
            except Exception as error:
                error = str(error)
                if error == "Signature has expired":
                    return {"message": "your token has been expired"}
                else:
                    raise InternalServerError({"message": "Internal Server Error"})

        Request = request.get_json()
        if not Request['username']  and not Request['password']:
            return {"message": "username or password is not define"}, 204
        else:
            user = Users.query.filter_by(username = Request['username'])
            if user.count() == 1: # CHECK IF USERNAME EXIST IN THE DATABASE
                password = bcrypt.hashpw(Request['password'].encode('UTF-8'), user.first().userpassword.encode('UTF-8'))
                if user.first().userpassword.encode('UTF-8') == password: # CHECK IF PASSWORD IS CORRECT
                    userType = get_user_type(user.first().id)
                    already_login = UsersLogs.query.filter_by(username = user.first().username)
                    if already_login.count() == 1:
                        update_active_user(public_id, datetime_now, already_login)
                        token = jwt.encode({'username': user.first().username, 'public_id' : public_id, 'exp': datetime_now + timedelta(days = 1)}, app.config['SECRET_KEY'])
                        token = token.decode('UTF-8')
                        return {'token': token, 'userType': userType}
                    elif already_login.count() == 0:
                        add_active_user(user.first().username, public_id, datetime_now)
                        token = jwt.encode({'username': user.first().username, 'public_id' : public_id, 'exp': datetime_now + timedelta(days = 1)}, app.config['SECRET_KEY'])
                        token = token.decode('UTF-8')
                        return {'token': token, 'userType': userType}
                else:
                    raise Unauthorized({"message": "could not verify"})
            else:
                raise Unauthorized({"message": "could not verify"})


class logout(Resource):
    def post(self):
        token = ''
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message' : 'token is missing'})

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            user = UsersLogs.query.filter_by(username = data['username']).one().status = "logout"
            db.session.commit()
            return 200
        except Exception as error:
            error = str(error)
            print("==>>",error)
            if error == "Signature has expired":
                raise InternalServerError({"message": "your token has been expired"})
            else:
                raise InternalServerError({"message": "Internal Server Error"})


def add_active_user(username, public_id, time_login):
    add = UsersLogs(username = username, public_id = public_id, time_login = time_login , last_request_time = time_login, status = "active", room_control_real_time_data = True)
    db.session.add(add)
    db.session.commit()


def update_active_user(public_id, time_login, user):
    user.one().public_id = public_id
    user.one().time_login = time_login
    user.one().last_request_time = time_login
    user.one().status = "active"
    db.session.commit()

def get_user_type(user_id):
    group_permission = []
    member = GroupMember.query.filter_by(user_id = user_id).all()
    print(member)
    if member == None:
        return "Guest"
    for queried_data in member:
        group = Group.query.filter_by(id = queried_data.group_id).first()
        permission = Permission.query.filter_by(id = group.permission_id).first()
        print(permission.name)
        group_permission.append(permission.name)
    print(group_permission,"==>")
    try:
        group_permission.index('Admin')
        return "Admin"
    except Exception as error:
        error = str(error)
        print(error)
    try:
        group_permission.index('User')
        return "User"
    except Exception as error:
        error = str(error)
        print(error)
    return "Guest"
