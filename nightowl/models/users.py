from nightowl.app import db
from sqlalchemy import ForeignKey
from nightowl.models.groupMember import GroupMember

#------
class Users(db.Model):
  __tablename__ = "users"
  id = db.Column(db.Integer, primary_key = True)
  username = db.Column(db.String(100), unique=True)
  userpassword = db.Column(db.String(100))
  Fname = db.Column(db.String(100))
  Lname = db.Column(db.String(100))
  cardID = db.Column(db.String(100), unique=True) 


  def __init__(self, username, userpassword, Fname,Lname, cardID):
    self.username = username
    self.userpassword = userpassword
    self.Fname = Fname
    self.Lname = Lname
    self.cardID = cardID    

  # def __repr__(self):
  #       return 'Users(username = {self.username!r}, userpassword = {self.userpassword!r}, Fname = {self.Fname!r}, Lname = {self.Lname!r}, cardID = {self.cardID}, public_id = {self.public_id})'.format(self=self)

