from flask import Flask, redirect, url_for, request,render_template,flash
from ..exceptions import UnauthorizedError, UnexpectedError
from nightowl.app import db
from ..auth.authentication import token_required
from flask_restful import Resource
from datetime import datetime

from nightowl.models.users import Users
from nightowl.models.room import Room
from nightowl.models.permission import Permission
from nightowl.models.auditTrail import AuditTrail

class auditTrail(Resource):
    @token_required
    def get(current_user, self):
        if current_user['userType'] == "Admin" or current_user['userType'] == "User":
            all_data = []
            query = AuditTrail.query.all()
            for queried_auditTrail in query:
                auditTrail = {}
                user = Users.query.filter_by(id = queried_auditTrail.user_id).first()
                room = Room.query.filter_by(id = queried_auditTrail.room_id).first()
                permission = Permission.query.filter_by(id = queried_auditTrail.permission_id).first()
                if user != None:
                    auditTrail['username'] = user.username
                    auditTrail['Fname'] = user.Fname
                else:
                    auditTrail['username'] = None
                    auditTrail['Fname'] = None
                if room != None:
                    auditTrail['room'] = room.name
                else:
                    auditTrail['room'] = None
                if permission != None:
                    auditTrail['permission'] = permission.name
                else:
                    auditTrail['permission'] = None
                auditTrail['timestamp'] = datetime.strftime(queried_auditTrail.timestamp,'%Y-%m-%d %I:%M %p')
                auditTrail['cardID'] = queried_auditTrail.cardID
                auditTrail['action'] = queried_auditTrail.action
                auditTrail['id'] = queried_auditTrail.id
                all_data.append(auditTrail)
            return {"auditTrail": all_data}
        else:
            raise UnauthorizedError()

class deleteAuditTrail(Resource):
    @token_required
    def delete(current_user, self,id):
        if current_user['userType'] == "Admin":
            AuditTrail.query.filter_by(id = id).delete()
            db.session.commit()
        else:
            raise UnauthorizedError()

class delAllAuditTrail(Resource):
    @token_required
    def delete(current_user,self):
        if current_user['userType'] == "Admin":
            AuditTrail.query.delete()
            db.session.commit()
        else:
            raise UnauthorizedError()
