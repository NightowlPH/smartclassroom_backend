from nightowl.models.group import Group
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields

class GroupSchema(ModelSchema):
    class Meta:
        model = Group

    permission_id = fields.Int()
