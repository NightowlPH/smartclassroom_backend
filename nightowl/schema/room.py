from nightowl.models.room import Room
from marshmallow_sqlalchemy import ModelSchema

class RoomSchema(ModelSchema):
	class Meta:
		model = Room
