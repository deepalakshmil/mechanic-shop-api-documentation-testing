
from application.extensions import ma
from application.models import Service_tickets
from marshmallow import fields

#====Schema =====#
class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    mechanics = fields.Nested("MechanicSchema",many=True)
    customer = fields.Nested("CustomerSchema")

    class Meta:
        model= Service_tickets
        # fields= ("mechanic_ids","VIN","customer_issue","service_date","customer_id","mechanics","customer","id")
        include_fk = True

      

# # === input schema (for POST only) ===

class ServiceTicketCreateSchema(ma.Schema):
    VIN           = fields.String(required=True)
    service_date  = fields.Date(required=True)
    customer_issue= fields.String(required=True)
    customer_id   = fields.Int(required=True)
    mechanic_ids  = fields.List(fields.Int(), required=True)


class EditServiceSchema(ma.Schema):
    add_mechanic_ids = fields.List(fields.Int(),required = True)
    remove_mechanic_ids = fields.List(fields.Int(),required = True)

    class Meta:
        fields = ("add_mechanic_ids","remove_mechanic_ids")


service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)

return_service_schema = ServiceTicketSchema(exclude = ['customer_id'])
edit_service_schema = EditServiceSchema()
service_ticket_create_schema = ServiceTicketCreateSchema()