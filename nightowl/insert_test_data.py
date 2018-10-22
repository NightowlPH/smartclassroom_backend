import csv
import bcrypt
from .app import db
from .models.users import Users
from .models.permission import Permission
from .models.group import Group
from .models.groupMember import GroupMember
from .models.room import Room
from .models.groupAccess import GroupAccess
from .models.roomStatus import RoomStatus
from .models.devices import Devices
from datetime import datetime
from .models.usersLogs import UsersLogs

def loadTestData():


	# CREATE TEST USERS
	with open('./resources/test_user.csv', 'rt') as csvfile:
		users = csv.reader(csvfile, delimiter=',')
		for user in users: 
			print(user)
			# password = bcrypt.hashpw(user[4].encode('UTF-8'), bcrypt.gensalt())
			# print(password)
			add = Users(username = user[0], userpassword = user[1], Fname = user[2], Lname = user[3], cardID = user[4])
			db.session.add(add)	
			db.session.commit()			
	# CREATE TEST PERMISSIONS		
	with open('./resources/test_permission.csv', 'rt') as csvfile:
		permissions = csv.reader(csvfile, delimiter=',')
		print("-----------------------------------------------------------")
		for permission in permissions:			
			print(permission)
			add = Permission(name = permission[0], description = permission[1])
			db.session.add(add)			

	# CREATE TEST ROOMS		
	with open('./resources/test_room.csv', 'rt') as csvfile:
		rooms = csv.reader(csvfile, delimiter=',')
		print("-----------------------------------------------------------")
		for room in rooms:			
			print(room)
			add = Room(name = room[0], description = room[1])
			db.session.add(add)			
			db.session.commit()
