from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api
from flask_cors import CORS, cross_origin
from flask_mqtt import Mqtt

app = Flask('nightowl', instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
api = Api(app)
if app.config['DEBUG']:
	CORS(app)

# app.config['MQTT_BROKER_URL'] = 'localhost'
# app.config['MQTT_BROKER_PORT'] = 1883
# app.config['MQTT_USERNAME'] = 'mark'
# app.config['MQTT_PASSWORD'] = 'pass'
# app.config['MQTT_REFRESH_TIME'] = 1.0  # refresh time in seconds
# mqtt = Mqtt(app)

# @mqtt.on_connect()
# def handle_connect(client, userdata, flags, rc):
#     mqtt.subscribe('test')

# @mqtt.on_message()
# def handle_mqtt_message(client, userdata, message):
#     data = dict(
#         topic=message.topic,
#         payload=message.payload.decode()
#     )
#     print("DATA",data)    


# @mqtt.on_log()
# def handle_logging(client, userdata, level, buf):
#     print(level, buf)

# class AllRoomStatus(Resource):
# 	def get(self):
# 		mqtt.publish("test","-----------------------HELLO----------------------------")
# 		return {"message": "yes"}

# api.add_resource(AllRoomStatus, '/test')


from nightowl.controllers.auditTrail import auditTrail,deleteAuditTrail, delAllAuditTrail
from nightowl.controllers.remoteDesign import AllRemoteDesign
from nightowl.controllers.devices import devices, device
from nightowl.controllers.login import login,logout
from nightowl.controllers.roomStatus import roomStatus, RoomStatusByID, AddDeviceToRoom
from nightowl.controllers.users import user, users, getUserProfile, editProfile, changePassword
from nightowl.controllers.permission import permission, permissions, getAllPer
from nightowl.controllers.group import groups, group, groupDetails
from nightowl.controllers.groupMember import groupMember,shwNotMem,deleteMember
from nightowl.controllers.room import rooms, room, roomDetails
from nightowl.controllers.groupAccess import groupAccess,shwNotGrpAccess, deleteGrpAccess
from nightowl.checkTag.checkTag import check_tag
from nightowl.controllers.routeGuard import routeGuard
from nightowl.controllers.register import register
from nightowl.controllers.usersLogs import activeUsers, delActiveUser

api.add_resource(login, '/login')
api.add_resource(logout, '/logout')

api.add_resource(users, '/users','/users/')
api.add_resource(user, '/user/<int:id>')
api.add_resource(editProfile, '/editProfile')

api.add_resource(permissions, '/permissions')
api.add_resource(permission, '/permission/<int:id>')
api.add_resource(getAllPer, '/getAllPermission')

api.add_resource(groups, '/groups')
api.add_resource(group, '/group/<id>')
api.add_resource(groupDetails, '/groupDetails/<id>')
api.add_resource(activeUsers, '/activeUsers')
api.add_resource(delActiveUser, '/activeUser/<int:id>')

api.add_resource(groupMember, '/groupMember/<int:id>')
api.add_resource(shwNotMem, '/shwNotMem/<int:id>')
api.add_resource(deleteMember, '/deleteMember/<int:id>/<int:user_id>')

api.add_resource(rooms, '/rooms')
api.add_resource(room, '/room/<int:id>')
api.add_resource(roomDetails, '/roomDetails/<int:id>')

api.add_resource(groupAccess, '/groupAccess/<int:id>')
api.add_resource(shwNotGrpAccess, '/shwNotGrpAccess/<int:id>')
api.add_resource(deleteGrpAccess, '/deleteGrpAccess/<int:id>')

api.add_resource(check_tag, '/checkTag/<string:room_name>/<string:cardID>')

api.add_resource(auditTrail, '/auditTrail')

api.add_resource(deleteAuditTrail, '/auditTrail/<int:id>')
api.add_resource(delAllAuditTrail,'/auditTrail/all')

api.add_resource(routeGuard, '/routeGuard')
api.add_resource(getUserProfile,'/getUserProfile')
api.add_resource(register, '/register')
api.add_resource(changePassword, '/changeUserPassword')

api.add_resource(devices, '/devices')
api.add_resource(device, '/device/<int:id>')

api.add_resource(roomStatus, '/RoomStatus')
api.add_resource(RoomStatusByID, '/roomStatus/<int:room_status_id>')
api.add_resource(AddDeviceToRoom, '/addRoomDevice/<int:room_id>')

api.add_resource(AllRemoteDesign, '/remoteDesign')


db.create_all()
