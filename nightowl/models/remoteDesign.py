from nightowl.app import db
from sqlalchemy import ForeignKey

class RemoteDesign(db.Model):
  __tablename__ = "remote_design"
  id = db.Column(db.Integer, primary_key = True)
  name = db.Column(db.String(100))
  description = db.Column(db.String(100))
  data = db.Column(db.JSON()) 

  def __init__(self,name,description, data):
    self.name = name
    self.description = description
    self.data = data


