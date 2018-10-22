from flask import Flask, redirect, url_for, request,render_template,flash
from flask import Blueprint
from nightowl.app import db
from ..auth.authentication import token_required
from flask_restful import Resource

from nightowl.models.groupAccess import GroupAccess
from nightowl.models.permission import Permission
from nightowl.models.group import Group
from nightowl.models.groupMember import GroupMember
from nightowl.models.room import Room

from nightowl.schema.groupAccess import groupAccess_schema
from nightowl.schema.group import GroupSchema


class groupAccess(Resource):
	@token_required
	def get(current_user, self, id):	
		if current_user['userType'] == "Admin" or current_user['userType'] == "User":	
			groupAccess = []
			query = GroupAccess.query.filter_by(room_id = id).all()		
			for queried_access in query:
				groupAccess.append({"id": queried_access.id, 
				"groupName": Group.query.filter_by(id = queried_access.group_id).first().name,
				"permissionName": Permission.query.filter_by(id = queried_access.permission_id).first().name,
				"users": GroupMember.query.filter_by(group_id = queried_access.group_id).count()})		
			return {"group": groupAccess}
		else:
			return 401

	@token_required
	def post(current_user, self, id):
		if current_user['userType'] == "Admin":
			request_data = request.get_json()		
			for data in request_data:									
				roomAccess = GroupAccess()
				roomAccess.room = Room.query.filter_by(id = id).first()
				roomAccess.group = Group.query.filter_by(id = data['group_id']).first()
				roomAccess.permission = Permission.query.filter_by(id = data['permission_id']).first()
				db.session.add(roomAccess)
				db.session.commit()			
		else:
			return 401

		
class shwNotGrpAccess(Resource):
	@token_required
	def get(current_user, self, id):
		if current_user == "Admin":
			counter = 0
			allGroup = []
			groups_schema = GroupSchema(only=('id','name'))
			group = Group.query.all()
			for queried_group in group:			
				if GroupAccess.query.filter_by(room_id = id, group_id = queried_group.id).count() == 0: 
					allGroup.append(groups_schema.dump(queried_group).data)
					allGroup[counter]["members"] = GroupMember.query.filter_by(group_id = queried_group.id).count()
					counter += 1
			return {"group": allGroup}
		else:
			return 401
	
class deleteGrpAccess(Resource):
	@token_required
	def delete(current_user, self,id):
		if current_user['userType'] == "Admin":
			query = GroupAccess.query.filter_by(id = id)		
			if query.count() == 1:
				query.delete()
				db.session.commit()				
			else:
				return {"message": "group not found"}
		else:
			return 401


