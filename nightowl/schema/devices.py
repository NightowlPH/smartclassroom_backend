from nightowl.models.devices import Devices
from marshmallow_sqlalchemy import ModelSchema

class DevicesSchema(ModelSchema):
	class Meta:
		model = Devices

devices_schema = DevicesSchema(only = ('id', 'name', 'description'))