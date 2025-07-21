from application.extensions import ma
from application.models import Mechanics


#====Schema =====#
class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model= Mechanics


mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
