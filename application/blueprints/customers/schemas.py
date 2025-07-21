
from application.extensions import ma
from application.models import Customer


#====Schema =====#
class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model= Customer 
       

customer_schema = CustomerSchema() 
customers_schema = CustomerSchema(many=True)
login_schema = CustomerSchema(exclude =['name','address','phone','salary'] ) 