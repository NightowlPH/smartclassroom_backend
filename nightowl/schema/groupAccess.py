from nightowl.models.groupAccess import GroupAccess
from marshmallow_sqlalchemy import ModelSchema

class GroupAccessSchema(ModelSchema):
	class Meta:
		model = GroupAccess

groupAccess_schema = GroupAccessSchema()