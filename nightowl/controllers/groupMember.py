from flask import Flask, redirect, url_for, request,render_template,flash
from werkzeug.exceptions import Unauthorized, InternalServerError
from flask import Blueprint
from nightowl.app import db
from ..auth.authentication import token_required
from flask_restful import Resource

from nightowl.models.groupMember import GroupMember
from nightowl.models.group import Group
from nightowl.models.users import Users

from nightowl.schema.users import UsersSchema

users_schema = UsersSchema(only=('id','username','Fname','Lname','cardID'))

class groupMember(Resource):
    @token_required
    def get(current_user, self, id):
        if current_user['userType'] == "Admin" or current_user['userType'] == "User":
            allUser = []
            query = GroupMember.query.filter_by(group_id = id).all()
            for queried_member in query:
                allUser.append(users_schema.dump(Users.query.filter_by(id = queried_member.user_id).first()).data)
            return {"members":allUser}
        else:
            raise Unauthorized()

    @token_required
    def post(current_user, self, id):
        if current_user['userType'] == "Admin":
            request_data = request.get_json()
            if len(request_data) !=0:
                for data in request_data:
                        member = GroupMember()
                        member.group = Group.query.filter_by(id = id).first()
                        member.user = Users.query.filter_by(id = data).first()
                        db.session.add(member)
                        db.session.commit()
            else:
                raise Unauthorized()
        else:
            raise Unauthorized()


class shwNotMem(Resource):
    @token_required
    def get(current_user, self, id):
        if current_user['userType'] == "Admin":
            allUser = []
            query = Users.query.all()
            for queried_user in query:
                if GroupMember.query.filter_by(group_id = id, user_id  = queried_user.id).count() == 0:
                    allUser.append(users_schema.dump(queried_user).data)
            return {"members": allUser}
        else:
            raise Unauthorized()


class deleteMember(Resource):
    @token_required
    def delete(current_user, self, id, user_id):
        if current_user['userType'] == "Admin":
            GroupMember.query.filter_by(group_id = id, user_id = user_id).delete()
            db.session.commit()
        else:
            raise Unauthorized()

















# user = Users.query.first()
        # group = Group.query.first()

        # group_member = GroupMember()
        # group_member.group = group
        # user.group_member.append(group_member)
        # db.session.add(user)
        # db.session.commit()
