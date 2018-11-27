from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api
from flask_cors import CORS, cross_origin
from nightowl.app import app, db, api
from flask_mqtt import Mqtt
from datetime import datetime

mqtt = Mqtt(app)

from nightowl.models.room import Room
from nightowl.models.devices import Devices
from nightowl.models.roomStatus import RoomStatus
from nightowl.models.remoteDesign import RemoteDesign

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
	mqtt.unsubscribe_all()	
	room_status = RoomStatus.query.all()	
	if len(room_status) != 0:		
		for queried_room_status in room_status:
			room = Room.query.filter_by(id = queried_room_status.room_id).first()
			device = Devices.query.filter_by(id = queried_room_status.device_id).first()
			remoteDesign = RemoteDesign.query.filter_by(id = device.remote_design_id).first()			
			mqtt.subscribe("smartclassroom/"+str(room.name)+"/"+str(device.name)+"/"+str(remoteDesign.ext_topic))			

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message): 
	da = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
	print("=================================================================>",da)
	topic=message.topic  
	topic = topic.replace('smartclassroom/','')
	payload=message.payload.decode()    
	datas = []
	data = ''    
	for character in topic:    	
		if character != '/':    		
			data += character    		
		else:    		
			datas.append(data)    		
			data = ''
	if len(datas) == 2:
	    room = Room.query.filter_by(name = datas[0]).first()
	    device = Devices.query.filter_by(name = datas[1]).first()    
	    if room != None and device != None:
	    	room_status = RoomStatus.query.filter_by(room_id = room.id, device_id = device.id)    	
	    	if room_status.first() != None:
	    		print(room.name+" "+device.name+" "+payload)   		
	    		room_status.one().status = str(payload)
	    		db.session.commit()
   


@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    print(level, buf)

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

class AllRoomStatus(Resource):
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

		

api.add_resource(AllRoomStatus, '/mqtt/roomStatus/<int:room_status_id>')
api.add_resource(AddDeviceToRoom, '/mqtt/addRoomDevice/<int:room_id>')  		

if __name__ == '__main__':	
	app.run(host='127.0.0.1', port=5001)