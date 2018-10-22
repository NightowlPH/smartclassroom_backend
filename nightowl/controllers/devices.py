from flask import Flask, redirect, url_for, request,render_template,flash
from flask import Blueprint
from nightowl.app import db
from ..auth.authentication import token_required
from flask_restful import Resource

from nightowl.models.devices import Devices
from nightowl.models.roomStatus import RoomStatus

from nightowl.schema.devices import devices_schema


class devices(Resource):
	@token_required
	def get(current_user, self):
		if current_user['userType'] == "Admin" or current_user['userType'] == "User":
			all_devices = []
			devices = Devices.query.all()
			for device in devices:
				all_devices.append(devices_schema.dump(device).data)
			return {'devices': all_devices}
		else:
			return 401

	@token_required
	def post(current_user, self):
		if current_user['userType'] == "Admin":
			Request = request.get_json()	
			addDevice = devices_schema.load(Request, session = db.session).data		
			if Devices.query.filter_by(name = addDevice.name).count() == 0:
				db.session.add(addDevice)
				db.session.commit()
			else:
				return {"message": "already exist", "token": current_user['token']}	
		else:
			return 401


class device(Resource):
	@token_required
	def delete(current_user, self, id):
		if current_user['userType'] == "Admin":
			if RoomStatus.query.filter_by(device_id = id).count() != 0:
				RoomStatus.query.filter_by(device_id = id).delete()			
			Devices.query.filter_by(id = id).delete()
			db.session.commit()
			return {"response":'device successfully deleted'}
		else:
			return 401


	@token_required
	def get(current_user, self, id):	
		if current_user['userType'] == "Admin" or current_user['userType'] == "User":				
			query = Devices.query.filter_by(id = id)

			if query.count() != 0:
				device = devices_schema.dump(query.first()).data
				return {"data": device}
			else:
				return {"data": []}	
		else:
			return 401

	@token_required
	def put(current_user, self, id):
		if current_user['userType'] == "Admin":
			request_data = request.get_json()

			query = Devices.query.filter_by(name = request_data['name'])
			if query.count() > 0 and int(id) != query.first().id:
				return{"message": "device already exist"}
			else:
				query = Devices.query.filter_by(id = id).one()
				query.name = request_data['name']
				query.description = request_data['description']
				db.session.commit()				
		else:
			return 401
