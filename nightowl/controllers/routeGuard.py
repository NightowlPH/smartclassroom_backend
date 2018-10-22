from flask import request
from flask_restful import Resource
from ..auth.authentication import token_required


class routeGuard(Resource):
	@token_required
	def get(current_user,self):
		return { "access": current_user['userType']}		
