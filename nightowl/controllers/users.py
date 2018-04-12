from flask import request
from nightowl.app import db
from flask_restful import Resource
import uuid
import bcrypt
import jwt

from ..auth.authentication import token_required

from nightowl.models.users import Users
from nightowl.models.groupMember import GroupMember
from nightowl.models.usersLogs import UsersLogs
from nightowl.models.group import Group

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
			return { "users": allUser, "token": current_user['token'] }						
		else:			
			return 401
		
	@token_required
	def post(current_user, self):	
		if current_user['userType'] == "Admin":	
			Request = request.get_json()	
			if not Request['username'] and not Request['userpassword'] and not Request['Lname'] and not Request['Fname'] and not Request['cardID']:
				return {"message": "some parameters is missing", "token": current_user['token']}
			if len(Request['userpassword']) < 10:
				return {"message": "password must be more than 10 characters", "token": current_user['token']} 					
			if Users.query.filter_by(username = Request['username']).count() == 0: #CHECK IF USER ALREADY EXIST
				addUser = Users(username = Request['username'], userpassword = bcrypt.hashpw(Request['userpassword'].encode('UTF-8'), bcrypt.gensalt()),
				                Lname = Request['Lname'], Fname = Request['Fname'], cardID = Request['cardID'])
				db.session.add(addUser)
				db.session.commit()			
				return {"message": "success", "token": current_user['token']}, 200
			else:
				return {'message': 'already exist', "token": current_user['token']}
		else:
			return 401


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
				return {"message": "user is currently login", "token": current_user['token']}			
			members = GroupMember.query.filter_by(user_id = id)	
			users = Users.query.filter_by(id = id)	
			if members.count() != 0:
				members.delete()			
			if users.count() == 1:
				users.delete()			
			db.session.commit()
			return {"token": current_user['token']}
			return {"token": current_user['token']}
		else:
			return 401

	@token_required
	def get(current_user, self, id): # GET USER INFO USING ID AND IT USE TO UPDATE USER		
		if current_user['userType'] == "Admin":
			query = Users.query.filter_by(id = id)
			if query.count() != 0:
				user = users_schema.dump(query.first()).data		
				return {"data": user, "token": current_user['token']}
			else:
				return {"response": "no user found", "token": current_user['token']}		
		else:			
			return 401

	@token_required
	def put(current_user, self, id):
		if current_user['userType'] == "Admin" or current_user['userType'] == "User":		
			data = request.get_json()							
			query = Users.query.filter_by(username = data['username'])
			query2 = Users.query.filter_by(cardID = data['cardID'])

			if query.count() > 0 and query.first().id != int(id):
				return { "message": "username already exist", "token": current_user['token']}

			elif query2.count() > 0 and query2.first().id != int(id):				
				return { "message": "cardID already exist", "token": current_user['token']}

			else:
				query = Users.query.filter_by(id = id).one()
				query.username = data['username']
				query.Lname = data['Fname']
				query.Lname = data['Lname']
				query.cardID = data['cardID']
				db.session.commit()
				return {"token": current_user['token']}, 201			
		else:
			return 401
		

class getUserProfile(Resource):	# THIS IS IN SIDEBAR HEADER
	def get(self):
		token = None
		if 'x-access-token' in request.headers:            
			token = request.headers['x-access-token']            

		if not token:            
			return jsonify({'message' : 'token is missing'})


		try:            
			data = jwt.decode(token, app.config['SECRET_KEY'])					
			active_user = UsersLogs.query.filter_by(public_id = data['public_id'], username = data['username']).first()
			user = Users.query.filter_by(username = active_user.username).first()  
			member = GroupMember.query.filter_by(user_id = user.id).first()
			group = Group.query.filter_by(id = member.group_id).first()			
			data = users_schema.dump(user).data
			if group.name[len(group.name)-1] == 's' or group.name[len(group.name)-1] == 'S':
				data['group_nameu'] = group.name[0:len(group.name)-1]
			else:
				data['group_name'] = group.name
			if active_user == None or user == None:
				return 401          
			return data
		except Exception as error: 			
			error = str(error)        
			print("==>",error)
			if error == "Signature has expired":				        
				return {"message": "your token has been expired"}, 500  
			else:
				return 500  


class changePassword(Resource):
	@token_required
	def post(current_user, self):
		print(current_user)
		if current_user['userType'] == "Admin" or current_user['userType'] == "User":	
			data = request.get_json()
			user = Users.query.filter_by(username = current_user['username'])
			if user == None:
				return 401		
			if len(data['new_password']) < 10:
				return {"message": "password must be more than 10 characters", "token": current_user['token']} 		
			password = bcrypt.hashpw(data['current_password'].encode('UTF-8'), user.first().userpassword.encode('UTF-8'))
			if user.first().userpassword.encode('UTF-8') != password:
				return {'message': 'invalid password', 'token' : current_user['token']}
			new_password = bcrypt.hashpw(data['new_password'].encode('UTF-8'), bcrypt.gensalt())
			user.one().userpassword = new_password
			db.session.commit()
			return {'message': 'your password is successfully change', 'token' : current_user['token']}
		else:
			return 401


		