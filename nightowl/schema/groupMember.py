from nightowl.models.groupMember import GroupMember
from marshmallow_sqlalchemy import ModelSchema

class GroupMemberSchema(ModelSchema):
	class Meta:
		model = GroupMember


groupMember_schema = GroupMemberSchema()
