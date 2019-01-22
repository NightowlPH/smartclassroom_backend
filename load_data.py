import sys
import csv
import bcrypt
from nightowl.app import db
from nightowl.models.users import Users
from nightowl.models.permission import Permission
from nightowl.models.group import Group
from nightowl.models.groupMember import GroupMember
from nightowl.models.room import Room
from nightowl.models.groupAccess import GroupAccess
from nightowl.models.roomStatus import RoomStatus
from nightowl.models.devices import Devices
from datetime import datetime
from nightowl.models.usersLogs import UsersLogs
from nightowl.models.remoteDesign import RemoteDesign

def loadData(dirname='data'):

    # CREATE TEST USERS
    with open('./{}/resources/user.csv'.format(dirname), 'rt') as csvfile:
        users = csv.reader(csvfile, delimiter=',')
        for user in users:
            print(user)
            # password = bcrypt.hashpw(user[1].encode('UTF-8'), bcrypt.gensalt())
            add = Users(username = user[0], userpassword = user[1], Fname = user[2], Lname = user[3], cardID = user[4], has_profile_picture = False)
            db.session.add(add)
            db.session.commit()

    # CREATE TEST PERMISSIONS
    with open('./{}/resources/permission.csv'.format(dirname), 'rt') as csvfile:
        permissions = csv.reader(csvfile, delimiter=',')
        print("-----------------------------------------------------------")
        for permission in permissions:
            print(permission)
            add = Permission(name = permission[0], description = permission[1])
            db.session.add(add)
            db.session.commit()

    # CREATE TEST GROUP
    with open('./{}/resources/group.csv'.format(dirname), 'rt') as csvfile:
        groups = csv.reader(csvfile, delimiter=',')
        print("-----------------------------------------------------------")
        for group in groups:
            print(group)
            add = Group(name = group[0], description = group[1])
            add.permission = Permission.query.filter_by(id = group[2]).first()
            db.session.add(add)
            db.session.commit()


    # CREATE TEST GROUP MEMBER
    add_group_member = GroupMember()
    add_group_member.group = Group.query.first()
    add_group_member.user = Users.query.filter_by(username = "mike").first()
    db.session.add(add_group_member)
    db.session.commit()

    # CREATE TEST ROOMS
    with open('./{}/resources/room.csv'.format(dirname), 'rt') as csvfile:
        rooms = csv.reader(csvfile, delimiter=',')
        print("-----------------------------------------------------------")
        for room in rooms:
            print(room)
            add = Room(name = room[0], description = room[1])
            db.session.add(add)
            db.session.commit()

    # CREATE TEST REMOTE DESIGN
    with open('./{}/resources/remote_design.csv'.format(dirname), 'rt') as csvfile:
        remote_designs = csv.reader(csvfile, delimiter='>')
        print("-----------------------------------------------------------")
        for remote_design in remote_designs:
            print(remote_design)
            add = RemoteDesign(name = remote_design[0], description = remote_design[1], data = remote_design[2], ext_topic = remote_design[3])
            db.session.add(add)
            db.session.commit()

    # CREATE TEST DEVICE
    with open('./{}/resources/device.csv'.format(dirname), 'rt') as csvfile:
        devices = csv.reader(csvfile, delimiter=',')
        print("-----------------------------------------------------------")
        for device in devices:
            print(device)
            add = Devices(name = device[0], description = device[1])
            add.remote_design = RemoteDesign.query.filter_by(id = int(device[2])).first()
            db.session.add(add)
            db.session.commit()

if __name__ == '__main__':
    if len(sys.argv)>1 and sys.argv[1] == 'test':
        loadData('instance')
    else:
        loadData()
