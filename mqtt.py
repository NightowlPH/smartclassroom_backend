from flask import Flask, request
from flask_mqtt import Mqtt
from nightowl.app import app, api
from flask_restful import Resource

from nightowl.models.roomStatus import RoomStatus
from nightowl.models.room import Room
from nightowl.models.devies import Devices

app.config['MQTT_BROKER_URL'] = 'localhost'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = 'mark'
app.config['MQTT_PASSWORD'] = 'passmord567'
app.config['MQTT_REFRESH_TIME'] = 1.0  # refresh time in seconds
mqtt = Mqtt(app)

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    room_status = RoomStatus.query.all()
    if len(room_status) != 0:
    	for queried_room_status in room_status:
    		room = Room.query.filter_by(id = queried_room_status.room_id).first()
    		device = Devices.query.filter_by(id = queried_room_status.device_id).first()
    		mqtt.subscribe("smartclassroom/"+str(room.name)+"/"+str(device.name)+"/on")


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )


class AllRoomStatus(Resource):
	def post(self, room_status_id):
		room_status = RoomStatus.query.filter_by(id = room_status_id)		
		if room_status.first() == None:
			return {"message": "room status not found"}
		room = Room.query.filter_by(id = room_status.first().room_id).first()
		device = Devices.query.filter_by(id = room_status.first().device_id).first()
		request_data = request.get_json()
		if request_data == True or request_data == "True":
			room_status.one().status == "on"
			mqtt.publish("smartclassroom/"+str(room.name)+"/"+str(device.name)+"/on", True)
		elif request_data == False or request_data == "False":
			room_status.one().status == "off"
			mqtt.publish("smartclassroom/"+str(room.name)+"/"+str(device.name)+"/on", False)
		else:
			return {"message": "invalid argument"}
		db.session.commit()


api.add_resource(AllRoomStatus, '/roomStatus')


