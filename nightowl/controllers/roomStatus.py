from flask import Flask, redirect, url_for, request,render_template,flash
from flask import Blueprint
from nightowl.app import db
from ..auth.authentication import token_required
from flask_restful import Resource
from datetime import datetime
from mqtt import mqtt
import json

from nightowl.models.roomStatus import RoomStatus
from nightowl.models.room import Room
from nightowl.models.devices import Devices
from nightowl.models.remoteDesign import RemoteDesign
from nightowl.models.usersLogs import UsersLogs


class roomStatus(Resource): # for angular frontend app
	@token_required
	def get(current_user, self):
		if current_user['userType'] == "Admin" or current_user['userType'] == "User":
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
					device_details = {
							"device_id": queried_room_device.device_id,
							"device_name": device.name,
							"device_status": queried_room_device.status,
							"room_status_id": queried_room_device.id,
							"remote_design": remote_design.name,
							"remote_design_id": remote_design.id,
							"class_name": class_name
						}
					if remote_design.name == "Temperature Slider":
						tem_details = json.loads(remote_design.data)
						device_details.update(tem_details)
					data['devices'].append(device_details)
				all_data["room_status"].append(data)
			return all_data
		else:
			return 401



class AllRoomStatus(Resource): # for mobile and other app
	@token_required
	def get(current_user, self):
		if current_user['userType'] == "Admin" or current_user['userType'] == "User":
			all_data = {"room_status": []}

			rooms = Room.query.all()
			totalDevice = Devices.query.count()	

			for room in rooms:
				data = {"room_id": room.id,"room_name": room.name.upper(), "devices": []}
				query = Devices.query.filter_by(name = "Door").first()
				room_device = RoomStatus.query.filter(RoomStatus.room_id == room.id, RoomStatus.device_id != query.id) # Ignore Door Device							
				for queried_room_device in room_device.all():
					device = Devices.query.filter_by(id = queried_room_device.device_id).first()					
					device_name = device.name
					device_status = queried_room_device.status					
					if device.name == "Aircon temperature":				
						device_name = "Temp."				
					if queried_room_device.status == "true":
						device_status = "on"
					elif queried_room_device.status == "false":
						device_status = "off"			
					device_details = {													
							"device_name": device_name,
							"device_status": device_status,							
						}					
					data['devices'].append(device_details)
				all_data["room_status"].append(data)
			return all_data
		else:
			return 401

class RoomStatusByRoomID(Resource):
	@token_required
	def get(current_user, self, id):
		if current_user['userType'] == "Admin" or current_user['userType'] == "User":

			room = Room.query.filter_by(id = id).first()
			data = {"room_id": room.id,"room_name": room.name, "date": datetime.strftime(datetime.today(),'%B %d %Y %A') , "devices": []}

			if room == None:
				return {"message": "room not found"}
			devices = RoomStatus.query.filter_by(room_id = room.id).all()
			for device in devices:
				queried_deivce = Devices.query.filter_by(id = device.device_id).first()				
				device_details = {			
						"room_status_id": device.id,				
						"device_name": queried_deivce.name,
						"device_status": device.status,							
					}
				if queried_deivce.name == "Aircon temperature":					
					if len(data['devices']) != 0:
						data['devices'].insert(0,device_details)
					else:
						data['devices'].append(device_details)
				else:					
					data['devices'].append(device_details)					
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
	@token_required	
	def post(current_user, self, room_id):
		if current_user['userType'] == "Admin":		
			room = Room.query.filter_by(id = room_id).first()
			data = request.get_json()

			if room == None:
					return {"message": "room not found"}
			for device_id in data:
				device = Devices.query.filter_by(id = device_id).first()
				remoteDesign = RemoteDesign.query.filter_by(id = device.remote_design_id).first()
				if device == None:
					return {"message": "device not found"}
				if remoteDesign.name == "Temperature Slider":				
					status = 24
				else:
					status = 'false'
				addDevice = RoomStatus(status = status, timestamp = datetime.today())
				addDevice.device = device
				addDevice.room = room							
				db.session.add(addDevice)
				db.session.commit()
				room_status = RoomStatus.query.all()
				# print(">>>>==================================",room_status,len(room_status))	
			mqtt.publish("smartclassroom/reloadMqtt","true")
				# print("ADD-->")
		else:
			return 401

class AllRoomStatusByID(Resource):
	@token_required	
	def put(current_user, self, room_status_id): #CONTROL DEVICES
		if current_user['userType'] == "Admin" or current_user['userType'] == "User":
			room_status = RoomStatus.query.filter_by(id = room_status_id).first()
			if room_status == None:
				return {"message": "room status not found"}

			payload = request.get_json()['value']
			print(type(payload),payload)
			if payload == True:
				payload = "true"
			elif payload == False:
				payload = "false"
			elif type(payload) == int and int(payload) >=16 and int(payload) <= 26:
				payload = int(payload)
			else:
				return {"message": "invalid payload"}
			data = get_room_status_details(room_status)		
			print("-----publish----")
			mqtt.publish("smartclassroom/"+str(data['room_name'])+"/"+str(data['device_name'])+"/"+str(data['ext_topic']),payload)						
		else:
			return 401		

	@token_required	
	def delete(current_user, self, room_status_id):
		if current_user['userType'] == "Admin":		
			room_status = RoomStatus.query.filter_by(id = room_status_id)
			if room_status.count() == 0:
				return {"message": "room device not found"}

			data = get_room_status_details(room_status.first())				
			room_status.delete()
			db.session.commit()
			mqtt.publish("smartclassroom/reloadMqtt","true")
			print("delete-->")
		else:
			return 401	

class Room_control_real_time_data(Resource):  # CHECK IF USER HAS REAL TIME IN ROOM CONTROL
	@token_required
	def get(current_user, self):
		if current_user['userType'] == "Admin" or current_user['userType'] == "User":
			user = UsersLogs.query.filter_by(username = current_user['username'])
			if user.count() == 0 or user.count() > 1:
				return {"message": "user is not currently login"}
			if user.first().room_control_real_time_data:
				return {"room_control_updated": True}
			if not user.first().room_control_real_time_data:
				user.one().room_control_real_time_data = True
				db.session.commit()
				return {"room_control_updated": False}
		else:
			return 401


def get_room_status_details(room_status):

	room = Room.query.filter_by(id = room_status.room_id).first()
	device = Devices.query.filter_by(id = room_status.device_id).first()
	remoteDesign = RemoteDesign.query.filter_by(id = device.remote_design_id).first()

	return {"room_name": room.name, "device_name": device.name, "ext_topic": remoteDesign.ext_topic}


