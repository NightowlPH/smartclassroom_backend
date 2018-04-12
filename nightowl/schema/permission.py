from nightowl.models.permission import Permission
from marshmallow_sqlalchemy import ModelSchema

class PermissionSchema(ModelSchema):
	class Meta:
		model = Permission
