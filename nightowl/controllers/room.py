from flask import Flask, redirect, url_for, request,render_template,flash
from flask import Blueprint
from nightowl.app import db
from ..auth.authentication import token_required
from flask_restful import Resource

from nightowl.schema.room import RoomSchema

from nightowl.models.room import Room
from nightowl.models.groupAccess import GroupAccess
from nightowl.models.roomStatus import RoomStatus

room_schema = RoomSchema(only = ( 'id', 'name', 'description' ))

class rooms(Resource):	
	@token_required
	def get(current_user, self):	
		if current_user['userType'] == "Admin" or current_user['userType'] == "User":	
			allRoom = []
			rooms = Room.query.all()
			for queried_room in rooms:
				data = room_schema.dump(queried_room).data
				data['groups'] = GroupAccess.query.filter_by(room_id = queried_room.id).count()	
				allRoom.append(data)
			return {"rooms": allRoom}
		else:
			return 401

	@token_required
	def post(current_user, self):	
		if current_user['userType'] == "Admin":
			Request = request.get_json()		
			addRoom = room_schema.load(Request, session = db.session).data			
			if Room.query.filter_by(name = addRoom.name).count() == 0:
				db.session.add(addRoom)
				db.session.commit()												
			else:
				return {"message": "already exist"}
		else:
			return 401

class room(Resource):
	@token_required
	def get(current_user, self, id):	
		if current_user['userType'] == "Admin" or current_user['userType'] == "User":	
			query = Room.query.filter_by(id = id)	
			if query.count() != 0:
				room = room_schema.dump(query.first()).data
				return {"data":room}
			else:
				return {"data": []}
		else:
			return 402


	@token_required
	def delete(current_user, self, id):
		if current_user['userType'] == "Admin":
			if RoomStatus.query.filter_by(room_id = id).count() != 0:
				RoomStatus.query.filter_by(room_id = id).delete()		
			if GroupAccess.query.filter_by(group_id = id).count() !=0:
				GroupAccess.query.filter_by(group_id = id).delete()			
			Room.query.filter_by(id = id).delete()
			db.session.commit()
			return {"response":'user successfully deleted'}
		else:
			return 401

	@token_required
	def put(current_user, self, id):
		if current_user['userType'] == "Admin":
			request_data = request.get_json()

			query = Room.query.filter_by(name = request_data['name'])
			if query.count() > 0 and int(id) != query.first().id:
				return{"message": "room already exist"}
			else:
				query = Room.query.filter_by(id = id).one()
				query.name = request_data['name']
				query.description = request_data['description']
				db.session.commit()				
		else:
			return 401


class roomDetails(Resource): # THIS IS USER IN NAVBAT
	@token_required
	def get(current_user, self, id):	
		if current_user == "Admin" or current_user == "User":	
			query = Room.query.filter_by(id = id)	
			if query.count() != 0:
				room = room_schema.dump(query.first()).data
				return {"data":room}
			else:
				return {"data": []}
		else:
			return 402