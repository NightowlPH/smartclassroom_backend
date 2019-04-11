from flask import request
from ..exceptions import UnauthorizedError
from nightowl.app import db
from ..auth.authentication import token_required
from flask_restful import Resource

from nightowl.schema.remoteDesign import remote_design_schema

from nightowl.models.remoteDesign import RemoteDesign


class AllRemoteDesign(Resource):
    @token_required
    def get(current_user, self):
        if current_user['userType'] == "Admin":
            all_data = {"remote_design": []}
            datas = RemoteDesign.query.all()
            for data in datas:
                all_data['remote_design'].append(remote_design_schema.dump(data).data)
            return all_data
        else:
            raise UnauthorizedError()
