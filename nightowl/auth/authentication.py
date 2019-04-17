from flask import make_response, request, jsonify, g
from werkzeug.exceptions import Unauthorized, InternalServerError
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
from ..exceptions import UnauthorizedError, UnexpectedError
import json

def login_user(request):
    token = ''
    if 'x-access-token' in request.headers:
        token = request.headers['x-access-token']
        url = str(request.url)

    log.debug("Token: {}".format(token))
    if not token:
        raise UnauthorizedError({'message' : 'token is missing'})
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'])
        log.debug("Token data: {}".format(data))
    except jwt.ExpiredSignatureError:
        raise UnexpectedError({"message": "your token has been expired"})
    except Exception:
        raise UnexpectedError("Error decoding token {}".format(token))

    user_log = UsersLogs.query.filter_by(public_id = data['public_id'],
                                         username = data['username'])
    try:
        user = Users.query.filter_by(username =data['username']).one()
    except:
        raise UnauthorizedError("User does not exist")
    user_log.one().last_request_time = datetime.strptime(datetime.strftime(datetime.today(),'%Y-%m-%d %I:%M %p'),'%Y-%m-%d %I:%M %p')
    db.session.commit()

    token = jwt.encode({'username': data['username'], 'public_id' : data['public_id'], 'exp': datetime.now() + timedelta(days = 1)}, app.config['SECRET_KEY'])
    token = token.decode('UTF-8')
    return user, token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user, token = login_user(request)
        g.current_user = user
        g.token = token
        code = 200
        ret = f(*args, **kwargs)
        if isinstance(ret, tuple):
            code = ret[1]
            ret = ret[0]
        response = make_response(json.dumps(ret), code)
        response.headers.extend({'x-access-token': token})
        log.debug("Response: {}".format(response))
        return response
    return decorated
