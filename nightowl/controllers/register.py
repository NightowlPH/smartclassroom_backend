from flask_restful import Resource
from flask import request
import uuid
import bcrypt

from nightowl.models.users import Users
from nightowl.app import db

class register(Resource):
	def post(self):
		Request = request.get_json()
		if not Request['username'] and not Request['userpassword'] and not Request['Lname'] and not Request['Fname'] and not Request['cardID']:
				return {"message": "some parameters is missing"}
		if len(Request['userpassword']) < 10:
			return {"message": "password must be more than 10 characters"} 					
		if Users.query.filter_by(username = Request['username']).count() == 0: #CHECK IF USER ALREADY EXIST
			addUser = Users(username = Request['username'], userpassword = bcrypt.hashpw(Request['userpassword'].encode('UTF-8'), bcrypt.gensalt()),
			Lname = Request['Lname'], Fname = Request['Fname'], cardID = Request['cardID'])
			db.session.add(addUser)
			db.session.commit()			
			return {"response": "success"}
		else:
			return {'response': 'already exist'}
