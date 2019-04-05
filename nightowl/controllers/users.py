from flask import request, send_file
from nightowl.app import db
from flask_restful import Resource
import uuid
import bcrypt
import jwt
import os

from ..auth.authentication import token_required

from nightowl.models.users import Users
from nightowl.models.groupMember import GroupMember
from nightowl.models.usersLogs import UsersLogs
from nightowl.models.group import Group
from nightowl.models.permission import Permission

from nightowl.app import app

from nightowl.schema.users import users_schema,addUsers_schema


class users(Resource):
	@token_required
	def get(current_user, self):
		allUser = []
		if current_user['userType'] == "Admin" or current_user['userType'] == "User":
			users = Users.query.filter(Users.username != current_user['username']).all()
			for queried_user in users:
				allUser.append(users_schema.dump(queried_user).data)
			return { "users": allUser }
		else:
			return 401

	@token_required
	def post(current_user, self):
		if current_user['userType'] == "Admin":
			Request = request.get_json()
			if not Request['username'] and not Request['userpassword'] and not Request['Lname'] and not Request['Fname'] and not Request['cardID']:
				return {"message": "some parameters is missing"}
			if len(Request['userpassword']) < 6:
				return {"message": "password must be more than 6 characters"}
			if Users.query.filter_by(username = Request['username']).count() == 0: #CHECK IF USER ALREADY EXIST
				addUser = Users(username = Request['username'], userpassword = bcrypt.hashpw(Request['userpassword'].encode('UTF-8'), bcrypt.gensalt()),
				                Lname = Request['Lname'], Fname = Request['Fname'], cardID = Request['cardID'], has_profile_picture = False)
				db.session.add(addUser)
				db.session.commit()
				return {"message": "success"}, 200
			else:
				return {'message': 'already exist'}
		else:
			return 401

class Get_account_photo(Resource):
	def put(self): #send user profile picture

		token = None
		if 'x-access-token' in request.headers:
			token = request.headers['x-access-token']

		if not token:
			return jsonify({'message' : 'token is missing'})

		try:
			data = jwt.decode(token, app.config['SECRET_KEY'])
			active_user = UsersLogs.query.filter_by(public_id = data['public_id'], username = data['username']).first()
			user = Users.query.filter_by(username = active_user.username).first()
			userType = get_user_type(user.id)
			if userType == "Admin" or userType == "User":

				if user == None:
					return {"message": "user not found"}
				if not user.has_profile_picture:
					return {"message": "user has no profile picture"}
				return send_file('image/user/'+str(user.id)+'.jpg', mimetype='image/jpg')
			else:
				return 401
		except Exception as error:
			error = str(error)
			print("user photo",error)
			if error == "Signature has expired":
				return {"message": "your token has been expired"}, 500
			else:
				return 500


class editProfile(Resource):
	def get(self): # GET USER INFO USING TOKEN
		token = None
		if 'x-access-token' in request.headers:
			token = request.headers['x-access-token']

		if not token:
			return jsonify({'message' : 'token is missing'})


		try:
			data = jwt.decode(token, app.config['SECRET_KEY'])
			active_user = UsersLogs.query.filter_by(public_id = data['public_id'], username = data['username']).first()
			user = Users.query.filter_by(username = active_user.username).first()
			return users_schema.dump(user)
		except Exception as error:
			error = str(error)
			print("editProfile",error)
			if error == "Signature has expired":
				return {"message": "your token has been expired"}, 500
			else:
				return 500



class user(Resource):
	@token_required
	def delete(current_user, self, id):
		if current_user['userType'] == "Admin":
			if UsersLogs.query.filter_by(username = Users.query.filter_by(id = id).first().username).first():
				return {"message": "user is currently login"}
			members = GroupMember.query.filter_by(user_id = id)
			users = Users.query.filter_by(id = id)
			if members.count() != 0:
				members.delete()
			if users.count() == 1:
				users.delete()
			db.session.commit()
		else:
			return 401

	@token_required
	def get(current_user, self, id): # GET USER INFO USING ID AND IT USE TO UPDATE USER
		if current_user['userType'] == "Admin":
			query = Users.query.filter_by(id = id)
			if query.count() != 0:
				user = users_schema.dump(query.first()).data
				return {"data": user}
			else:
				return {"response": "no user found"}
		else:
			return 401

	@token_required
	def put(current_user, self, id):
		if current_user['userType'] == "Admin" or current_user['userType'] == "User":
			query = Users.query.filter_by(username = request.values['username'])
			query2 = Users.query.filter_by(cardID = request.values['cardID'])

			if query.count() > 0 and query.first().id != int(id):
				return { "message": "username already exist"}

			elif query2.count() > 0 and query2.first().id != int(id):
				return { "message": "cardID already exist"}

			else:

				try:
					file = request.files['Image']
					if query.first().has_profile_picture:
						os.remove("nightowl/image/user/"+str(id)+".jpg")
					image_file_name = str(id)+"."+'jpg'
					file.save(os.path.join('nightowl/image/user', image_file_name))
					photo = True
				except Exception as e:
					photo = False
					print(e,"error")

