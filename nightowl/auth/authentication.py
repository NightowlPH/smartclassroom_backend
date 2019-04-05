from flask import make_response, request, jsonify
from functools import wraps
from datetime import datetime, timedelta
import jwt
from nightowl.app import db
import uuid
import logging

log = logging.getLogger(__name__)

from ..models.users import Users
from ..models.usersLogs import UsersLogs
from ..models.group import Group
from ..models.groupMember import GroupMember
from ..models.permission import Permission
from ..app import app
import json

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = ''
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
            url = str(request.url)

        if not token:
            return jsonify({'message' : 'token is missing'})
        log.debug("Token: {}".format(token))
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            log.debug("Token data: {}".format(data))
            user_log = UsersLogs.query.filter_by(public_id = data['public_id'],username = data['username'])
            user = Users.query.filter_by(username =data['username'])
            if user.count() == 0 and user_log.count() == 0: # CHECK IF USER EXIST
                return 401
            elif user.count() == 1 and user_log.count() == 1:
                userType = get_user_type(user.first().id)
                user_log.one().last_request_time = datetime.strptime(datetime.strftime(datetime.today(),'%Y-%m-%d %I:%M %p'),'%Y-%m-%d %I:%M %p')
                db.session.commit()

                code = 200
                ret = f({"userType": userType,'username': user.first().username}, *args, **kwargs)
                if isinstance(data, tuple):
                    code = ret[1]
                    ret = ret[0]
                response = make_response(json.dumps(ret), code)
                token = jwt.encode({'username': data['username'], 'public_id' : data['public_id'], 'exp': datetime.now() + timedelta(days = 1)}, app.config['SECRET_KEY'])
                token = token.decode('UTF-8')
                response.headers.extend({'x-access-token': token})
                log.debug("Response: {}".format(response))
                return response
            else:
                return 401
        except Exception as error:
            log.error("An error occured in checking the token.")
            log.exception(error)
            if error == "Signature has expired":
                return {"message": "your token has been expired"}, 500
            else:
                return {"message": "Internal Server Error"}, 500

    return decorated



def get_user_type(user_id):
    group_permission = []
    memberships = GroupMember.query.filter_by(user_id = user_id).all()
    if memberships == None:
        return "Guest"
    for group_member in memberships:
        group_permission.append(group_member.group.permission.name)
    try:
        group_permission.index('Admin')
        return "Admin"
    except Exception as error:
        error = str(error)
    try:
        group_permission.index('User')
        return "User"
    except Exception as error:
        error = str(error)
        print(error)

    return "Guest"
