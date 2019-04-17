from flask import request, g
from flask_restful import Resource
from ..auth.authentication import token_required


class routeGuard(Resource):
    @token_required
    def get(self):
        current_user = g.current_user
        return { "access": current_user.userType}
