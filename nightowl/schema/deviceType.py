from nightowl.models.deviceType import DeviceType
from marshmallow_sqlalchemy import ModelSchema

class DeviceTypeSchema(ModelSchema):
	class Meta:
		model = DeviceType

deviceType_schema = DeviceTypeSchema()