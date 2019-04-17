from flask import Flask, redirect, url_for, request,render_template,flash, g
from ..exceptions import UnauthorizedError, UnexpectedError
from flask import Blueprint
from nightowl.app import db
from ..auth.authentication import token_required
from flask_restful import Resource
import jwt

from nightowl.models.permission import Permission
from nightowl.models.groupAccess import GroupAccess
from nightowl.models.usersLogs import UsersLogs
from nightowl.models.users import Users
from nightowl.schema.permission import PermissionSchema
from nightowl.app import app


class permissions(Resource):
    @token_required
    def get(self):
        current_user = g.current_user
        if current_user.userType == "Admin" or current_user.userType == "User":
            allPermission = []
            permission_schema = PermissionSchema(only = ('id', 'name', 'description'))
            permission = Permission.query.all()
            for queried_permission in permission:
                allPermission.append(permission_schema.dump(queried_permission).data)
            return {"permissions": allPermission}
        else:
            raise UnauthorizedError()

    @token_required
    def post(self):
        current_user = g.current_user
        if current_user.userType == "Admin":
            permissions_schema = PermissionSchema()

            Request = request.get_json()
            addPermission = permissions_schema.load(Request, session = db.session).data
            if Permission.query.filter_by(name = addPermission.name).count() == 0:
                db.session.add(addPermission)
                db.session.commit()
            else:
                return {"message": "already exist"}
        else:
            raise UnauthorizedError()

class permission(Resource):
    @token_required
    def delete(self, id):
        current_user = g.current_user
        if current_user.userType == "Admin":
            if GroupAccess.query.filter_by(permission_id = id).count() != 0:
                GroupAccess.query.filter_by(user_id = id).delete()
            Permission.query.filter_by(id = id).delete()
            db.session.commit()
            return {"response":'permission successfully deleted'}
        else:
            raise UnauthorizedError()

    @token_required
    def get(self, id):
        current_user = g.current_user
        if current_user.userType == "Admin" or current_user.userType == "User":
            permission_schema = PermissionSchema(only = ('name', 'description'))
            query = Permission.query.filter_by(id = id)

            if query.count() != 0:
                permission = permission_schema.dump(query.first()).data
                return {"data": permission}
            else:
                return {"data": []}
        else:
            raise UnauthorizedError()

    @token_required
    def put(self, id):
        current_user = g.current_user
        if current_user.userType == "Admin":
            request_data = request.get_json()

            query = Permission.query.filter_by(name = request_data['name'])
            if query.count() > 0 and int(id) != query.first().id:
                return{"message": "permission already exist"}
            else:
                query = Permission.query.filter_by(id = id).one()
                query.name = request_data['name']
                query.description = request_data['description']
                db.session.commit()
        else:
            raise UnauthorizedError()



class getAllPer(Resource):
    @token_required
    def get(self):
        current_user = g.current_user
        allPermission = []
        permission_schema = PermissionSchema(only = ('id', 'name', 'description'))
        permission = Permission.query.all()
        for queried_permission in permission:
            allPermission.append(permission_schema.dump(queried_permission).data)
        return {"permissions": allPermission}
