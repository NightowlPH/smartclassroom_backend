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

if __name__ == '__main__':	
	app.run(host='127.0.0.1', port=8002)