from nightowl.app import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from nightowl.models.permission import Permission

class Group(db.Model):
	__tablename__ = "group"
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(100), unique = True)
	description = db.Column(db.String(100))
	permission_id = db.Column(db.Integer, ForeignKey('permission.id'))

	permission = db.relationship("Permission", backref = "group")

	def __init__(self, name, description):
		self.name = name
		self.description = description

	def __repr__(self):
		return 'Group( name = {self.name!r}, description = {self.description})'.format(self=self)



