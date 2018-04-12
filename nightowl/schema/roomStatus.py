from nightowl.models.roomStatus import RoomStatus
from marshmallow_sqlalchemy import ModelSchema

class RoomStatusSchema(ModelSchema):
  class Meta:
    model = RoomStatus

roomStatus_schema = RoomStatusSchema()