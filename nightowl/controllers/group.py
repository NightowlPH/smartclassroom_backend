from flask import request, g
from ..exceptions import UnauthorizedError, UnexpectedError, InvalidDataError
from nightowl.app import db
from ..auth.authentication import token_required
from flask_restful import Resource
from datetime import datetime
import logging

from ..models.group import Group
from nightowl.models.groupAccess import GroupAccess
from nightowl.models.groupMember import GroupMember
from nightowl.models.room import Room
from nightowl.models.permission import Permission
from sqlalchemy import and_

log = logging.getLogger(__name__)

from nightowl.schema.group import GroupSchema

class groups(Resource):
    @token_required
    def get(self):
        current_user = g.current_user
        groups_schema = GroupSchema(only=('id','name', 'description', 'permission_id'))
        if current_user.userType == "Admin" or current_user.userType == "User":
            allGroup = []
            group = Group.query.all()
            for queried_group in group:
                data = groups_schema.dump(queried_group).data
                data['members'] = GroupMember.query.filter_by(group_id = queried_group.id).count()
                data['permission_name'] = queried_group.permission.name
                allGroup.append(data)
            return {"groups":allGroup}
        else:
            raise UnauthorizedError()

    @token_required
    def post(self):
        current_user = g.current_user
        print("PASS ADD GROUP")
        if current_user.userType == "Admin":
            data = request.get_json()
            print("--------------",data)
            if Group.query.filter_by(name = data['name']).count() == 0:
                group = Group(name = data['name'], description = data['description'])
                global_access = GroupAccess()
                global_access.group = group
                global_access.permission = Permission.query.filter_by(id = int(data['permission_id'])).first()
                db.session.add(group)
                db.session.commit()
            else:
                raise InvalidDataError("already exist")
        else:
            raise UnauthorizedError()

class group(Resource):
    @token_required
    def delete(self, id):
        current_user = g.current_user
        if current_user.userType == "Admin":
            query = Group.query.filter_by(name = "Guard").first()
            if GroupMember.query.filter_by(group_id = id).count() != 0:
                GroupMember.query.filter_by(group_id = id).delete()
            elif GroupAccess.query.filter_by(group_id = id).count() !=0:
                GroupAccess.query.filter_by(group_id = id).delete()
            Group.query.filter_by(id = id).delete()
            db.session.commit()
            return {"response":'user successfully deleted'}
        else:
            raise UnauthorizedError()

    @token_required
    def get(self, id):
        current_user = g.current_user
        if current_user.userType == "Admin" or current_user.userType == "User":
            groups_schema = GroupSchema(only=('id','name', 'description', "permission_id"))
            query = Group.query.filter_by(id = id)
            if query.count() != 0:
                group = groups_schema.dump(query.first()).data
                group['permission_name'] = query.first().permission.name
                return {"data": group}
            else:
                return {"data": []}
        else:
            raise UnauthorizedError()

    @token_required
    def put(self, id):
        current_user = g.current_user
        if current_user.userType == "Admin":
            request_data = request.get_json()
            log.debug("Request data: {}".format(request_data))
            query = Group.query.filter_by(name = request_data['name'])
            if query.count() > 0 and int(id) != query.first().id:
                raise InvalidDataError("group already exist")

            if 'permission_id' in request_data.keys() and \
                    Permission.query.get(request_data['permission_id'])is None:
                raise InvalidDataError("permission type does not exit")
            else:
                group = Group.query.get(id)
                group.name = request_data['name']
                group.description = request_data['description']
                if 'permission_id' in request_data:
                    permid = request_data['permission_id']
                    group.permission = Permission.query.get(permid)
                db.session.commit()
        else:
            raise UnauthorizedError()

class groupDetails(Resource): # THIS IS USER IN NAVBAT
    @token_required
    def get(self, id):
        current_user = g.current_user
        if current_user.userType == "Admin" or current_user.userType == "User":
            groups_schema = GroupSchema(only=('id','name', 'description'))
            query = Group.query.filter_by(id = id)
            if query.count() != 0:
                group = groups_schema.dump(query.first()).data
                return {"data": group}
            else:
                return {"data": []}
        else:
            raise UnauthorizedError()






# room = Room.query.first()
# permission1 = Permission.query.first()
# group1 = Group.query.first()

# group_access = GroupAccess()
# group_access.group = group1
# group_access.permission = permission1
# room.group_access.append(group_access)
# db.session.add(room)
# db.session.commit()
