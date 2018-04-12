from nightowl.models.users import Users
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields

class UsersSchema(ModelSchema):
	class Meta:
		model = Users

users_schema = UsersSchema(only=('id','username','Fname','Lname','cardID'))
addUsers_schema = UsersSchema()