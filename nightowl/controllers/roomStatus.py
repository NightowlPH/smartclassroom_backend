from flask import Flask, redirect, url_for, request,render_template,flash
from flask import Blueprint
from nightowl.app import db
from ..auth.authentication import token_required
from flask_restful import Resource
from datetime import datetime
from mqtt import mqtt

from nightowl.models.roomStatus import RoomStatus
from nightowl.models.room import Room
from nightowl.models.devices import Devices
from nightowl.models.remoteDesign import RemoteDesign


class roomStatus(Resource): # for angular frontend app
	@token_required
	def get(current_user, self):
		if current_user['userType'] == "Admin":
			all_data = {"room_status": []}

			rooms = Room.query.all()
			totalDevice = Devices.query.count()	

			for room in rooms:
				data = {"room_id": room.id,"room_name": room.name, "devices": []}
				room_device = RoomStatus.query.filter_by(room_id = room.id)			
				add_device = True
				if room_device.count() == totalDevice:
					add_device = False
				data['add_device'] = add_device
				for queried_room_device in room_device.all():
					device = Devices.query.filter_by(id = queried_room_device.device_id).first()
					remote_design = RemoteDesign.query.filter_by(id = device.remote_design_id).first()
					class_name = ""
					if remote_design.name == "Switch2":
						class_name = "Door"					
					data['devices'].append({
							"device_id": queried_room_device.device_id,
							"device_name": device.name,
							"device_status": queried_room_device.status,
							"room_status_id": queried_room_device.id,
							"remote_design": remote_design.name,
							"remote_design_id": remote_design.id,
							"class_name": class_name
						})
				all_data["room_status"].append(data)
			return all_data
		else:
			return 401



class AllRoomStatus(Resource): # for mobile and other app
	@token_required
	def get(current_user, self):
		if current_user['userType'] == "Admin":
			data = []

			room_status = RoomStatus.query.all()
			for queried_room_status in room_status:
				status = 'True'
				if queried_room_status.status == "False":
					status = 'False'
				data.append({"id": queried_room_status.id, "status": status})
			return data
		else:
			return 401

class RoomStatusByID(Resource): # for mobile and other app
	@token_required
	def get(current_user, self, room_status_id):
		if current_user['userType'] == "Admin":
			room_status = RoomStatus.query.filter_by(id = room_status_id).first()
			if room_status == None:
				return {"message": "room status not found"}
			return {"id": room_status.id, "status": room_status.status}
		else:
			401	


class GetDeviceToAdd(Resource):
	@token_required
	def get(current_user, self, room_id): # get all device not is not added to the room
		if current_user['userType'] == "Admin":
			data = {"devices": []}

			devices = Devices.query.all()
			for device in devices:
				query = RoomStatus.query.filter_by(room_id = room_id, device_id = device.id).count()
				if query == 0:
					data['devices'].append({
							"id": device.id,
							"name": device.name,
							"description": device.description
						})
			return data
		else:
			return 401

class AddDeviceToRoom(Resource):	
	def post(self, room_id):		
		room = Room.query.filter_by(id = room_id).first()
		data = request.get_json()

		if room == None:
				return {"message": "room not found"}
		for device_id in data:
			device = Devices.query.filter_by(id = device_id).first()
			remoteDesign = RemoteDesign.query.filter_by(id = device.remote_design_id).first()
			if device == None:
				return {"message": "device not found"}
			addDevice = RoomStatus(status = 'False', timestamp = datetime.today())
			addDevice.device = device
			addDevice.room = room
			mqtt.subscribe("smartclassroom/"+str(room.name)+"/"+str(device.name)+"/"+str(remoteDesign.ext_topic))			
			db.session.add(addDevice)
			db.session.commit()
			print("ADD-->")			

class AllRoomStatusByID(Resource):
	def put(self, room_status_id):
		room_status = RoomStatus.query.filter_by(id = room_status_id).first()
		if room_status == None:
			return {"message": "room status not found"}

		payload = request.get_json()['value']
		data = get_room_status_details(room_status)		

		mqtt.publish("smartclassroom/"+str(data['room_name'])+"/"+str(data['device_name'])+"/"+str(data['ext_topic']),payload)		

	def delete(self, room_status_id):		
		room_status = RoomStatus.query.filter_by(id = room_status_id)
		if room_status.count() == 0:
			return {"message": "room device not found"}

		data = get_room_status_details(room_status.first())		
		mqtt.unsubscribe("smartclassroom/"+str(data['room_name'])+"/"+str(data['device_name'])+"/"+str(data['ext_topic']))		
		room_status.delete()
		db.session.commit()
		print("delete-->")		

def get_room_status_details(room_status):

	room = Room.query.filter_by(id = room_status.room_id).first()
	device = Devices.query.filter_by(id = room_status.device_id).first()
	remoteDesign = RemoteDesign.query.filter_by(id = device.remote_design_id).first()

	return {"room_name": room.name, "device_name": device.name, "ext_topic": remoteDesign.ext_topic}


