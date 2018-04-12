from nightowl.models.auditTrail import AuditTrail
from marshmallow_sqlalchemy import ModelSchema

class AuditTrailSchema(ModelSchema):
	class Meta:
		model = AuditTrail

auditTrial_schema = AuditTrailSchema()