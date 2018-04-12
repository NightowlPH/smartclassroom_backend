from flask import request
from nightowl.app import db
from ..auth.authentication import token_required
from flask_restful import Resource
from datetime import datetime

from ..models.group import Group
from nightowl.models.groupAccess import GroupAccess
from nightowl.models.groupMember import GroupMember
from nightowl.models.room import Room
from nightowl.models.permission import Permission

from nightowl.schema.group import GroupSchema

class groups(Resource):
	@token_required
	def get(current_user, self):
		groups_schema = GroupSchema(only=('id','name', 'description', 'permission_id'))		
		if current_user['userType'] == "Admin" or current_user['userType'] == "User":			
			allGroup = []
			group = Group.query.all()						
			for queried_group in group:				
				data = groups_schema.dump(queried_group).data
				data['members'] = GroupMember.query.filter_by(group_id = queried_group.id).count()								
				permission = Permission.query.filter_by(id = queried_group.permission_id).first()
				data['permission_name'] = permission.name
				allGroup.append(data)
			return {"groups":allGroup, "token": current_user['token']}		
		else:
			return 401

	@token_required
	def post(current_user, self):
		print("PASS ADD GROUP")
		if current_user['userType'] == "Admin":
			data = request.get_json()	
			print("--------------",data)										
			if Group.query.filter_by(name = data['name']).count() == 0:
				group = Group(name = data['name'], description = data['description'])			
				group.permission = Permission.query.filter_by(id = int(data['permission_id'])).first()	
				db.session.add(group)
				db.session.commit()
				return {"token": current_user['token']}
			else:
				return {"message": "already exist", "token": current_user['token']}	
		else:
			return 401	

class group(Resource):
	@token_required
	def delete(current_user, self, id):
		if current_user['userType'] == "Admin":
			query = Group.query.filter_by(name = "Guard").first()
			if GroupMember.query.filter_by(group_id = id).count() != 0:
				GroupMember.query.filter_by(group_id = id).delete()			
			elif GroupAccess.query.filter_by(group_id = id).count() !=0:
				GroupAccess.query.filter_by(group_id = id).delete()			
			Group.query.filter_by(id = id).delete()
			db.session.commit()
			return {"response":'user successfully deleted', "token": current_user['token']}			
		else:
			return 401

	@token_required
	def get(current_user, self, id):	
		if current_user['userType'] == "Admin" or current_user['userType'] == "User":		
			groups_schema = GroupSchema(only=('id','name', 'description','permission_id'))			
			query = Group.query.filter_by(id = id)
			if query.count() != 0:
				group = groups_schema.dump(query.first()).data
				permission = Permission.query.filter_by(id = group['permission_id']).first()
				group['permission_name'] = permission.name
				return {"data": group, "token": current_user['token']}
			else:
				return {"data": [], "token": current_user['token']}
		else:
			return 401		

	@token_required
	def put(current_user, self, id):
		if current_user['userType'] == "Admin":		
			request_data = request.get_json()			
			query = Group.query.filter_by(name = request_data['name'])
			if query.count() > 0 and int(id) != query.first().id:
				return{"message": "group already exist", "token": current_user['token']}
			if Permission.query.filter_by(id = request_data['permission_id']).first() == None:
				return{"message": "permission type does not exit", "token": current_user['token']}
			else:
				query = Group.query.filter_by(id = id).one()
				query.name = request_data['name']
				query.description = request_data['description']
				query.permission_id = Permission.query.filter_by(id = request_data['permission_id']).first().id
				db.session.commit()
				return {"token": current_user['token']}
		else:
			return 401

class groupDetails(Resource): # THIS IS USER IN NAVBAT
	@token_required
	def get(current_user, self, id):		
		if current_user == "Admin" or current_user == "User":		
			groups_schema = GroupSchema(only=('id','name', 'description'))			
			query = Group.query.filter_by(id = id)
			if query.count() != 0:
				group = groups_schema.dump(query.first()).data
				return {"data": group}
			else:
				return {"data": []}
		else:
			return 401






# room = Room.query.first()
# permission1 = Permission.query.first()
# group1 = Group.query.first()

# group_access = GroupAccess()		
# group_access.group = group1
# group_access.permission = permission1
# room.group_access.append(group_access)
# db.session.add(room)
# db.session.commit()