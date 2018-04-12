from nightowl.app import db
from nightowl.models.roomStatus import RoomStatus

class DeviceType(db.Model):
  __tablename__ = "device_type"
  id = db.Column(db.Integer, primary_key = True)
  name = db.Column(db.String(100), unique = True)
  description = db.Column(db.String(100))


  def __init__(self, name, description):
    self.name = name
    self.description = description