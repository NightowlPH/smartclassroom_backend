from flask import make_response, request, jsonify
from functools import wraps
from datetime import datetime
import jwt
from nightowl.app import db
import uuid

from ..models.users import Users
from ..models.usersLogs import UsersLogs
from ..models.group import Group
from ..models.groupMember import GroupMember
from ..models.permission import Permission
from ..app import app

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = ''        
        if 'x-access-token' in request.headers:            
            token = request.headers['x-access-token'] 
            url = str(request.url)           

        if not token:            
            return jsonify({'message' : 'token is missing'})                

        try:            
            data = jwt.decode(token, app.config['SECRET_KEY'])                       
            user_log = UsersLogs.query.filter_by(public_id = data['public_id'],username = data['username'])        
            user = Users.query.filter_by(username =data['username'])            
            if user.count() == 0 and user_log.count() == 0: # CHECK IF USER EXIST
                return 401
            elif user.count() == 1 and user_log.count() == 1:            
                userType = get_user_type(user.first().id)                                                        
                user_log.one().last_request_time = datetime.strptime(datetime.strftime(datetime.today(),'%Y-%m-%d %I:%M %p'),'%Y-%m-%d %I:%M %p')
                db.session.commit()
                return f({"userType": userType,'username': user.first().username}, *args, **kwargs) 
            else:
                return 401                                       
        except Exception as error:   
            error = str(error)        
            print("==>>",error)
            if error == "Signature has expired":                
                return {"message": "your token has been expired"}, 500  
            else:
                return {"message": "Internal Server Error"}, 500         

    return decorated



def get_user_type(user_id):
    group_permission = []
    member = GroupMember.query.filter_by(user_id = user_id).all()
    if member == None:
        return "Guest"
    for queried_data in member:
        group = Group.query.filter_by(id = queried_data.group_id).first()
        permission = Permission.query.filter_by(id = group.permission_id).first()
        group_permission.append(permission.name)
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